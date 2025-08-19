#
//  insertdataclass.py
//  
//
//  Created by Thomas (Vu) H. Tran on 8/18/25.
//
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    email: str = ""  # optional field with default value

# Creating an instance of the data class
person1 = Person(name="Alice", age=30, email="alice@example.com")
print(person1)
