
# Mojo Language Examples Reference

## Basic Types and Variables
```mojo
let immutable_value: Int = 42
var mutable_value: String = "Hello"
let float_val: Float64 = 3.14159
let bool_val: Bool = True
```

## Functions
```mojo
fn add(x: Int, y: Int) -> Int:
    return x + y

fn greet(name: String) -> String:
    return "Hello, " + name + "!"
    
# Generic function
fn swap[T](inout a: T, inout b: T):
    let temp = a
    a = b
    b = temp
```

## Structs
```mojo
struct Point:
    var x: Float64
    var y: Float64
    
    fn __init__(inout self, x: Float64, y: Float64):
        self.x = x
        self.y = y
        
    fn distance(self, other: Point) -> Float64:
        let dx = self.x - other.x
        let dy = self.y - other.y
        return sqrt(dx * dx + dy * dy)
```

## Collections
```mojo
# Dynamic Vector
var vec = DynamicVector[Int]()
vec.append(1)
vec.append(2)
vec.append(3)

# Dictionary
var dict = Dict[String, Int]()
dict["one"] = 1
dict["two"] = 2

# Iteration
for i in range(len(vec)):
    print(vec[i])
```

## Error Handling
```mojo
fn divide(a: Float64, b: Float64) raises -> Float64:
    if b == 0:
        raise Error("Division by zero")
    return a / b

try:
    let result = divide(10, 0)
except e:
    print("Error:", e)
```

## Memory Management
```mojo
# Manual memory allocation
let ptr = Pointer[Int].alloc(10)
for i in range(10):
    ptr.store(i, i * i)
    
# Don't forget to free
ptr.free()

# RAII pattern with structs
struct Buffer:
    var data: Pointer[UInt8]
    var size: Int
    
    fn __init__(inout self, size: Int):
        self.data = Pointer[UInt8].alloc(size)
        self.size = size
        
    fn __del__(owned self):
        self.data.free()
```

## SIMD Operations
```mojo
from math import sqrt
from algorithm import vectorize

fn euclidean_distance(x: DynamicVector[Float32], y: DynamicVector[Float32]) -> Float32:
    var sum: Float32 = 0.0
    
    @parameter
    fn vector_dist[simd_width: Int](idx: Int):
        let diff = x.load[width=simd_width](idx) - y.load[width=simd_width](idx)
        sum += (diff * diff).reduce_add()
        
    vectorize[vector_dist, 16](len(x))
    return sqrt(sum)
```

## Python Interop
```mojo
from python import Python

fn use_numpy():
    let np = Python.import_module("numpy")
    let array = np.array([1, 2, 3, 4, 5])
    let mean = np.mean(array)
    print("Mean:", mean)
    
fn use_requests():
    let requests = Python.import_module("requests")
    let response = requests.get("https://api.example.com/data")
    let data = response.json()
    return data
```

## Async/Parallel
```mojo
from algorithm import parallelize

fn parallel_compute(data: DynamicVector[Float64]) -> Float64:
    var results = DynamicVector[Float64](len(data))
    
    @parameter
    fn compute_chunk(idx: Int):
        results[idx] = expensive_computation(data[idx])
        
    parallelize[compute_chunk](len(data))
    
    # Reduce results
    var total = 0.0
    for r in results:
        total += r
    return total
```

## Pattern Matching (Future)
```mojo
# Note: Pattern matching syntax may evolve
fn process_value(val: Variant) -> String:
    match val:
        case Int(x):
            return "Integer: " + str(x)
        case String(s):
            return "String: " + s
        case Float64(f):
            return "Float: " + str(f)
        case _:
            return "Unknown type"
```
