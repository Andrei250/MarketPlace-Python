"""
This module offers the available Products.

Computer Systems Architecture Course
Assignment 1
March 2022
"""

import uuid
import logging
import time
from logging.handlers import RotatingFileHandler
from threading import Lock
from random import randint

# configuration of logging file
logging.Formatter.converter = time.gmtime
logging.basicConfig(filename="marketplace.log", level=logging.DEBUG)
HANDLER = RotatingFileHandler(filename='marketplace.log', maxBytes=2048 * 1024, backupCount=8)
TIME_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
HANDLER.setFormatter(TIME_FORMATTER)
LOGGER = logging.getLogger()
LOGGER.addHandler(HANDLER)

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    maximumCartValue = 9999999 # constant used for generating cart id

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """

        self.size_per_producer = queue_size_per_producer
        self.producers = {} # for each id, I have an entry into the dict
        self.producer_ids_lock = Lock()
        self.cart_ids_lock = Lock()
        self.carts = {} # all the carts available
        self.cart_lock = Lock() # lock used for operations over cart

    def register_producer(self):
        """
        Returns an id for the producer that calls this.

        if one or many threads access this method I need to keep it safe on
        generation, using a lock.
        """
        logging.info("Entered register_producer method")

        id_prod = None
        try:
            with self.producer_ids_lock:
                id_prod = uuid.uuid4().hex

                while id_prod in self.producers:
                    id_prod = uuid.uuid4().hex

            self.producers[id_prod] = []

            logging.info("Leaving register_producer method")
            return id_prod
        except ValueError as exc:
            logging.error("Error in register_producer: %s", str(exc))
            return None

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.

        if the producer is not assigned or its queue is full return False.
        otherwise add the product into queue and return True.
        Mark the product as not used.
        """
        logging.info('Entered publish method with params %s and %s',
                     str(producer_id), str(product))

        if not producer_id in self.producers:
            logging.error("In publish method producer_id does not exist")
            return False

        if len(self.producers[producer_id]) == self.size_per_producer:
            logging.info("In publish method producer_id has the queue full")
            return False

        try:
            self.producers[producer_id].append([product, 0])

            logging.info("Leaving publish method")
            return True
        except ValueError as exc:
            logging.error("Error foudn in publish: %s", str(exc))
            return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id

        Random get an id from 0 to maximum value.
        I use a mutex to block the acces to this part of code.
        This way I am sure that there will be no race conditions.
        """
        cart_id = None
        logging.info("Entering new_cart method")

        try:
            with self.cart_ids_lock:
                cart_id = randint(0, Marketplace.maximumCartValue)

                while cart_id in self.carts:
                    cart_id = randint(0, Marketplace.maximumCartValue)

            self.carts[cart_id] = []

            logging.info("Leaving new_cart method")
            return cart_id
        except ValueError as exc:
            logging.error("Error in new_cart: %s", str(exc))
            return None

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again

        Go through each item in the dictionare and if the product is there
        then add it into the cart and delete it from the queue.
        I also add the id of the producer in case of removing.
        Mark as used.
        """
        logging.info('Entered add_to_cart method with params %s and %s',
                     str(cart_id), str(product))

        try:
            with self.cart_lock:
                for key, value in self.producers.items():
                    for prod in value:
                        if product == prod[0]:
                            self.carts[cart_id].append((product, key))
                            prod[1] = 1
                            logging.info("Leaving add_to_cart method. Product added")
                            return True

            logging.info("Leaving add_to_cart method. Product is not into the store")
            return False
        except ValueError as exc:
            logging.error("Error in add_to_cart: %s", str(exc))
            return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        logging.info('Entered remove_from_cart method with params %s and %s',
                     str(cart_id), str(product))

        # go through products and find one of its kind
        try:
            with self.cart_lock:
                for tpl in self.carts[cart_id]:
                    if tpl[0] == product:
                        self.carts[cart_id].remove(tpl)

                        # remove element from producer's queue
                        # I used a for loop, because maybe the indexes
                        # will be lost
                        for _, value in self.producers.items():
                            for prod in value:
                                if product == prod[0]:
                                    prod[1] = 0

                        logging.info("Leaving remove_from_cart method")
                        return

            logging.info("Leaving remove_from_cart method")
        except ValueError as exc:
            logging.error("Error in remove_from_cart: %s", str(exc))

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        logging.info('Entered place_order method with params %s', str(cart_id))

        answer = []

        # go through the cart and get first item which is the product
        try:
            for item in self.carts[cart_id]:
                answer.append(item[0])

                with self.cart_lock:
                    for value in self.producers.items():
                        for prod in enumerate(value):
                            if item[0] == prod[0]:
                                del prod

        except ValueError as exc:
            logging.error("Error in place_order: %s", str(exc))

        logging.info('Leaving place_order method')
        return answer
