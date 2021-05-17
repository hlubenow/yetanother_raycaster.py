### yetanother_raycaster.py
Python translation of a ray casting tutorial in C

Ray casting is the technique that was used to create early 1990s 3D games such as the original game "Doom" by "id Software".

From a player avatar in a 2D environment, several hundred "rays" are sent out to measure the distances to 2D obstacles (walls).
The resulting data is then used to create a 3D projection of the environment. Each ray is used to draw a vertical "slice" of a wall. By drawing several hundred slices at the correct positions, a real-time image of the surroundings can be created.

The developer "3DSage" has provided a nice [tutorial video on Youtube](https://www.youtube.com/watch?v=gYRrGTC7GtA) about the subject.
He uses C and the OpenGL library. His code can be found [here](https://github.com/3DSage/OpenGL-Raycaster_v1).

First, I translated his tutorial code from C to PyOpenGL while trying to stay as close to his version as possible.

Then I wrote a Pygame version, that is a bit more free (but does the same thing).

My project uses the MIT License, because the original code uses that license.
