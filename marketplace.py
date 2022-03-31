"""
This module represents the Marketplace.

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
        self.producerIdsLock = Lock()
        self.cartIdsLock = Lock()
        self.carts = {} # all the carts available

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        # if one or many threads access this method I need to keep it rafe on
        # generation
        self.producerIdsLock.acquire()
        id = uuid.uuid4().hex
        
        while id in self.producers:
            id = uuid.uuid4().hex
        
        self.producerIdsLock.release()
        
        self.producers[id] = []
        
        return id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
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
        """
        self.cartIdsLock.acquire()
        cart_id = randint(0, Marketplace.maximumCartValue)
        
        while cart_id in self.carts:
            cart_id = randint(0, Marketplace.maximumCartValue)

        self.cartIdsLock.release()
        
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
        """
        for id, products in self.producers:
            if product in products:
                self.carts[cart_id].append((product, id))
                self.producers[id].remove(product)
                
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
        for tuple in self.carts[cart_id]:
            if tuple[0] == product:
                self.producers[tuple[1]].append(product)
                self.carts[cart_id].remove(tuple)
                return

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        return self.carts[cart_id]
    
    def destroy_cart(self, cart_id):
        if not cart_id in self.carts:
            return
        
        self.carts.remove(cart_id)
