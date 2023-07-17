STEP 1:
Design an ObjectMgr which manages a pool of objects. Objects can be considered to be ints (from 1 to n). It should provide api’s to get_object() and free_object():

get_object(): Returns any object available in the pool. An object cannot be given away again unless it has been freed.


free_object(int obj): Returns the object back to the pool so that it can be given out again.

Please document the API’s definitions, data structures and write tests.

STEP 2:
1. Write a GraphQL API schema to use the above functions to create, get and free objects.
2. Deploy it as a service/container that can be used to deploy on a linux server.


## How to run

```shell
git clone github.com/Koshkaj/tromzoAssignment
cd tromzoAssignment

make run
```

`make run ` spins up a container maps it out to the default port that is defined in the `Makefile`

`make test` will run the unit tests that are written to this assignment
