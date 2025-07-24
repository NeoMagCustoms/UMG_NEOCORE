from modular.html import Button, Div
from modular.behavior import on_click

# Atomic kernel: opens a hidden modal div
pub fn modal_button_kernel():
    open_btn = Button("Open Modal", id="openModal")
    modal    = Div("This is a modal", id="modal", style="display:none")

    @on_click(target="openModal")
    fn show_modal():
        modal.style.display = "block"

    return (open_btn, modal)
