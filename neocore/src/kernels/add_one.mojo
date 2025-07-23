@compiler.register("AddOne")
struct AddOne:
    @staticmethod
    fn execute(x: Float32) -> Float32:
        return x + 1
