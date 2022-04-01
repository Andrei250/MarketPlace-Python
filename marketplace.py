"""
This module offers the available Products.

Computer Systems Architecture Course
Assignment 1
March 2022
"""

import uuid
from threading import Lock
from random import randint

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
        self.consumers = {} # for each consumer, I have an entry into the dict
        self.producer_ids_lock = Lock()
        self.cart_ids_lock = Lock()
        self.carts = {} # all the carts available

    def register_producer(self):
        """
        Returns an id for the producer that calls this.

        if one or many threads access this method I need to keep it safe on
        generation, using a lock.
        """
        id_prod = None

        with self.producer_ids_lock:
            id_prod = uuid.uuid4().hex

            while id_prod in self.producers:
                id_prod = uuid.uuid4().hex

        self.producers[id_prod] = []

        return id_prod

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
        """
        if not producer_id in self.producers:
            return False

        if len(self.producers[producer_id]) == self.size_per_producer:
            return False

        self.producers[producer_id].append(product)

        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id

        Random get an id from 0 to maximum value.
        I use a mutex to block the acces to this part of code.
        This way I am sure that there will be no race conditions.
        """
        cart_id = None

        with self.cart_ids_lock:
            cart_id = randint(0, Marketplace.maximumCartValue)

            while cart_id in self.carts:
                cart_id = randint(0, Marketplace.maximumCartValue)

        self.carts[cart_id] = []

        return cart_id

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
        """
        for key, value in self.producers.items():
            if product in value:
                self.carts[cart_id].append((product, key))
                value.remove(product)

                return True

        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        # go through products and find one of its kind
        for tpl in self.carts[cart_id]:
            if tpl[0] == product:
                self.producers[tpl[1]].append(product)
                self.carts[cart_id].remove(tpl)
                return

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        answer = []

        # go through the cart and get first item which is the product
        for item in self.carts[cart_id]:
            answer.append(item[0])

        return answer
