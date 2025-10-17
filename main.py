import sys
import os
import importlib
import matrices
import tkinter as tk
from tkinter import filedialog, messagebox

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random

import filetypes
handlers = {}
for m in filetypes.__all__:
    importlib.import_module('filetypes.' + m).register(handlers)

import Mesh

global mesh
mesh = None

scaleFactor = 1.05
rotateFactor = 0.05
translateFactor = 0.05

# Gets called by glutMainLoop() many times per second
def doIdle():
    pass  # Remove if we actually use this function

def doKeyboard(*args):  # Not working
    pass
    doRedraw()

def doSpecial(*args):
    global cameraMatrix
    if glutGetModifiers() & GLUT_ACTIVE_SHIFT:
        if args[0] == GLUT_KEY_UP:
            cameraMatrix = cameraMatrix * matrices.translate(0, -translateFactor, 0)  # up
        if args[0] == GLUT_KEY_DOWN:
            cameraMatrix = cameraMatrix * matrices.translate(0, translateFactor, 0)  # down
        if args[0] == GLUT_KEY_LEFT:
            cameraMatrix = cameraMatrix * matrices.translate(translateFactor, 0, 0)  # left
        if args[0] == GLUT_KEY_RIGHT:
            cameraMatrix = cameraMatrix * matrices.translate(-translateFactor, 0, 0)  # right
    elif glutGetModifiers() & GLUT_ACTIVE_CTRL:
        if args[0] == GLUT_KEY_UP:
            cameraMatrix = cameraMatrix * matrices.scale(1/scaleFactor, 1/scaleFactor, 1/scaleFactor)
        if args[0] == GLUT_KEY_DOWN:
            cameraMatrix = cameraMatrix * matrices.scale(scaleFactor, scaleFactor, scaleFactor)
    else:
        if args[0] == GLUT_KEY_UP:
            cameraMatrix = cameraMatrix * matrices.rotateX(-rotateFactor)  # up
        if args[0] == GLUT_KEY_DOWN:
            cameraMatrix = cameraMatrix * matrices.rotateX(rotateFactor)  # down
        if args[0] == GLUT_KEY_LEFT:
            cameraMatrix = cameraMatrix * matrices.rotateY(-rotateFactor)  # left
        if args[0] == GLUT_KEY_RIGHT:
            cameraMatrix = cameraMatrix * matrices.rotateY(rotateFactor)  # right
    doRedraw()

# Called by glutMainLoop() when window is resized
def doReshape(width, height):
    global cameraMatrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glViewport(0, 0, width, height)
    gluPerspective(45.0, float(width) / height, .1, 200)
    doCamera()

def doCamera():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    orientationMatrix = cameraMatrix.copy()
    orientationMatrix[3] = matrices.Vector4d(0, 0, 0, 1)
    pos = matrices.Vector4d(0, 3, 10, 1) * cameraMatrix
    lookAt = matrices.Vector4d(0, 0, 0, 1) * cameraMatrix
    direction = matrices.Vector4d(0, 1, 0, 1) * orientationMatrix

    gluLookAt(*(pos.list()[:-1] + lookAt.list()[:-1] + direction.list()[:-1]))

# Called by glutMainLoop() when screen needs to be redrawn
def doRedraw():
    doCamera()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, (.25, .25, .25, 1.0))
    glMaterial(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, .5))
    glMaterial(GL_FRONT_AND_BACK, GL_SHININESS, (128.0,))
    glMatrixMode(GL_MODELVIEW)

    if mesh:
        mesh.draw()

    glutSwapBuffers()

def open_ply_file():
    global mesh
    file_path = filedialog.askopenfilename(
        title="Open .ply File",
        filetypes=[("PLY files", "*.ply")],
    )
    if file_path:
        try:
            ext = os.path.splitext(file_path)[1][1:]  # e.g., "ply"
            mesh = handlers[ext](file_path)  # Use the appropriate loader
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load mesh:\n{e}")
    else:
        print("No file selected.")

def create_gui():
    root = tk.Tk()
    root.title("PLY File Viewer")

    open_button = tk.Button(root, text="Open", command=open_ply_file)
    open_button.pack(pady=20, padx=50)

    root.geometry("200x100")
    root.after(0, lambda: None)
    root.destroy()

if __name__ == '__main__':
    global cameraMatrix
    cameraMatrix = matrices.getIdentity4x4()
    create_gui()

    # Basic initialization - the same for most apps
    glutInit([])
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 480)
    glutCreateWindow(b"Simple OpenGL Renderer")
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glClearColor(0.1, 0.1, 0.2, 0.0)

    # Set up two lights
    glEnable(GL_LIGHTING)
    BRIGHT4f = (1.0, 1.0, 1.0, 1.0)
    DIM4f = (.2, .2, .2, 1.0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, BRIGHT4f)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, BRIGHT4f)
    glLightfv(GL_LIGHT0, GL_POSITION, (10, 10, 10, 0))
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT1, GL_AMBIENT, DIM4f)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, DIM4f)
    glLightfv(GL_LIGHT1, GL_POSITION, (-10, 10, -10, 0))
    glEnable(GL_LIGHT1)

    # Callback functions
    glutDisplayFunc(doRedraw)
    glutIdleFunc(doIdle)
    glutReshapeFunc(doReshape)
    glutSpecialFunc(doSpecial)
    glutKeyboardFunc(doKeyboard)

    glutMainLoop()
