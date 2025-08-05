from memory import memset_zero, memcpy
from python import Python
from utils.variant import Variant

@compiler.register("cache.memory.get")
struct Get:
    """
    Implements get for memory
    Category: memory
    Type: Instruction
    """
    
    var config: Dict[String, Variant]
    var state: Dict[String, Variant]
    
    fn __init__(inout self):
        self.config = Dict[String, Variant]()
        self.state = Dict[String, Variant]()
    
    @staticmethod
    fn execute(inout self, input: Variant) -> Variant:
        """Execute the get operation"""
        
        # Get from cache
        let key = input.get_string("key")
        
        if key in self.state:
            let entry = self.state[key]
            # Check if expired
            let expiry = entry.get_int("expiry", 0)
            let now = self._get_timestamp()
            
            if expiry == 0 or now < expiry:
                return entry.get("value")
                
        return Variant(None)
        
    fn configure(inout self, config: Dict[String, Variant]):
        """Configure the block with given parameters"""
        self.config = config
        
    fn get_state(self) -> Dict[String, Variant]:
        """Get current block state"""
        return self.state