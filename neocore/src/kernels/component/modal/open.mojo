from memory import memset_zero, memcpy
from python import Python
from utils.variant import Variant

@compiler.register("component.modal.open")
struct Open:
    """
    Implements open for modal
    Category: modal
    Type: Instruction
    """
    
    var config: Dict[String, Variant]
    var state: Dict[String, Variant]
    
    fn __init__(inout self):
        self.config = Dict[String, Variant]()
        self.state = Dict[String, Variant]()
    
    @staticmethod
    fn execute(inout self, input: Variant) -> Variant:
        """Execute the open operation"""
        
        # Open modal component
        let modal_id = input.get_string("id", "modal")
        let content = input.get_string("content", "")
        
        # Set modal state
        self.state["open"] = Variant(True)
        self.state["content"] = Variant(content)
        self.state["id"] = Variant(modal_id)
        
        # Return render data
        return Variant({
            "html": self._render_modal(modal_id, content),
            "open": True
        })
        
    fn configure(inout self, config: Dict[String, Variant]):
        """Configure the block with given parameters"""
        self.config = config
        
    fn get_state(self) -> Dict[String, Variant]:
        """Get current block state"""
        return self.state