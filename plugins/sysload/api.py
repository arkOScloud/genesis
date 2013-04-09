from genesis.apis import API
from genesis.com import Interface


class SysStat(API):
    class ISysStat(Interface):
        def get_load(self):
            pass
        
        def get_ram(self):
            pass
            
        def get_swap(self):
            pass

   