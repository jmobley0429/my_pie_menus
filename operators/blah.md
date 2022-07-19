Hey All, I have a question about asyncio, I have a program in Blender that basically slices objects into chunks depending on one of 3 axes. I am trying to get the addon to run each loop asynchronously, but wait for each loop to finish in the meantime. e.g.:

```python
if self.x:
    # do an async loop to  slice on the x axis a number of times
    loop.as_completed(slice_x())
if self.y:
    # only when and if all slice_x loops are completed, then start y_loop
    loop.as_completed(slice_x())
if self.z:
    # etc
    loop.as_completed(slice_z())

```
I feel like what's happening at the moment is that i'm using asyncio.gather to run lists
of coroutines, but each of the 3 loops is getting ahead of itself in some areas.

For instance

```python
# simplified version of my code as it stands now
async def slice_axis(axis, index):
  print(f"Slicing-{axis} Object Number {index}")

async def slice_loop():
  for axis in list('xyz'):
    coros = [slice_axis(axis, i+1) for i in range(3)]
    await asyncio.gather(*coros)

loop = async.get_event_loop()
loop.as_completed(slice_loop())
```

My code like this is currently giving me this result:

# each object is kind of running ahead through the loops on their own,
# as each slice is done.
>>> Slicing-x Object Number 1
>>> Slicing-y Object Number 1
>>> Slicing-x Object Number 2
>>> Slicing-z Object Number 1
>>> Slicing-y Object Number 2
etc....

When I need it more to be like:
# doesnt matter the order of each object as long as the axes are grouped together.
>>> Slicing-x Object Number 1
>>> Slicing-x Object Number 2
>>> Slicing-x Object Number 3

>>> Slicing-y Object Number 2
>>> Slicing-y Object Number 1
>>> Slicing-y Object Number 3

>>> Slicing-z Object Number 2
>>> Slicing-z Object Number 3
>>> Slicing-z Object Number 1

Because The problem lies in my algorithm needing to sort and delete old objects and keep track of which ones need to be sliced and are already sliced etc, It's getting to the part where the code is calling for it to delete an object while it's looping on the z axis, that that hasn't even been sliced fully on the y-axis yet and throwing an Exception because it can't find that object.

Or at least, that's what I believe to be the case.

Here is the attached relevant chunk of code from my script.

```python

async def async_slice(self, context, loc, index, outlist=None):
  # the async slicing function, self.current_loc is from a
  # list of vectors based on object dimensions, self.index keeps
  # track of what object and location we are on.
    self.current_loc = loc
    self.current_index = index
    result = await self._slice_operation(context)
    if result == "":
        return False
    if outlist:
        # each object is duplicated and sliced into it's new form,
        # then appended to the next list to be sliced on the next axis
        outlist.append(self.current_obj)
      return True

# forgive me if this is a little redundant, I didn't design it from
# the ground up to be async, only decided on it after the fact when
# performance was subpar.

async def slice_x():
    self.current_axis = "x"
    x_locs = self.slice_locs[self.current_axis]

    coros = [self.async_slice(context, loc, index, outlist=self.sliced_x) for index, loc in enumerate(x_locs)]
    await asyncio.gather(*coros)

async def slice_y():
    self.current_axis = "y"
    y_locs = self.slice_locs[self.current_axis]
    # like here, if user didn't choose to slice on the x-axis, we just pretend
    # the sliced_x list was just the first object all along.
    if not self.sliced_x:
        self.sliced_x = [self.obj]
    for obj in self.sliced_x:
        self.obj = obj
        coros = [
            self.async_slice(context, loc, index, outlist=self.sliced_y) for index, loc in enumerate(y_locs)
        ]
        await asyncio.gather(*coros)
        # once this object has been duplicated and sliced the required number of
        # it can be deleted.
        context.collection.objects.unlink(obj)

async def slice_z():
    self.current_axis = "z"
    z_locs = self.slice_locs[self.current_axis]
    # same deal, if user only chose z then the slice_y is just the first obj.
    # else if they chose x and z, then pretend that sliced_y is sliced_x
    # without actually slicing y.
    if not self.sliced_y:
        if not self.sliced_x:
            self.sliced_y = [self.obj]
        else:
            self.sliced_y = self.sliced_x
    for obj in self.sliced_y:
        self.obj = obj
        coros = [self.async_slice(context, loc, index) for index, loc in enumerate(z_locs)]
        await asyncio.gather(*coros)
        context.collection.objects.unlink(obj)

  ```

  Thanks for any help you can offer.
