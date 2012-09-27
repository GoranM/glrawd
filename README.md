GLrawd
======

A Blender scene exporter, which provides geometry data for OpenGL applications, in a convenient binary format.

---

Format
------

```c
// Structure of the .rawd file:
//
// [ count_v | verts* | count_i | indices* | count_n | nodes* ]
//
// Basic import example:

typedef struct {
	float mat_world[16]; // world transform matrix
	GLuint offset_idx;   // where indices for this Geom node start
	GLuint count_idx;    // how many to consume
} Geom;

GLuint* count_verts = (GLuint*)fileLoad("scene.rawd"); // Loads entire file into memory, and returns pointer to that memory
GLfloat* verts = (GLfloat*)(count_verts + 1);
GLuint* count_indices = (GLuint*)(verts + (*count_verts * 3)); // 1 vert -> 3 floats
GLuint* indices = count_indices + 1;
GLuint* count_nodes = indices + *count_indices;
Geom* nodes = (Geom*)(count_nodes + 1);

```

---

Install and Use
---------------

The io_scene_rawd.py script is a valid Blender addon, and can therefore be installed as one: In the "User Preferences" window, click "Install Addon", select the io_scene_rawd.py script, click "Install Addon", and then simply enable it.

You can now see a new "GLrawd(.rawd)" option in File -> Export.
