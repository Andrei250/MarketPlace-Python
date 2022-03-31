"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep

class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        Thread.__init__(self, **kwargs)

        self.carts = carts
        self.marketplace = marketplace
        self.wait_time = retry_wait_time
        self.name = kwargs['name']
        self.cart = None

    def run(self):
        for cart in self.carts:
            id = self.marketplace.new_cart()
        
            for items in cart:
                while items['qty'] > 0:
                    is_available = None
                    
                    if items['type'] == 'add':
                        is_available = self.marketplace.add_to_cart(id,
                                                                items['prod'])
                        
                        if is_available == True:
                            items['qty'] -= 1
                        else:
                            sleep(self.wait_time)
                        
                    elif items['type'] == 'remove':
                        is_available = self.marketplace.remove_from_cart(id,
                                                                    items['prod'])
                        items['qty'] -= 1
                    
                    
        
            items = self.marketplace.place_order()
            self.marketplace.destroy_cart(id)
            
            
