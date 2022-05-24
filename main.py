import os
from enum import Enum
from types import CellType
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders
import math
import numpy
import pyrr
from PIL import Image
from SkyBox import SkyBox
from Texture import Texture
from Camera import Camera
from Ground import Ground
from Map import Map
from Map import ObjectType
import random
import time

xPosPrev = 0
yPosPrev = 0
firstCursorCallback = True
sensitivity = 0.05

def cursorCallback(window, xPos, yPos):
	global firstCursorCallback
	global sensitivity
	global xPosPrev, yPosPrev
	if firstCursorCallback:
		firstCursorCallback = False	
	else:
		xDiff = xPos - xPosPrev
		yDiff = yPosPrev - yPos
		camera.rotateUpDown(yDiff * sensitivity)
		camera.rotateRightLeft(xDiff * sensitivity)

	xPosPrev = xPos
	yPosPrev = yPos

def mouseButtonCallback(window, button, action, mods):
	"""kocka lerakasa bal egergombra """
	if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
		cellFrontX, cellFrontZ = camera.getFrontCellPosition(20)
		if not world.isSomething(cellFrontZ, cellFrontX):
			try: 
				world.table[cellFrontZ][cellFrontX] = world.getObjectType("BOX")
			except IndexError: pass


	"""kockak visszaszedese jobb egergombra"""
	if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.PRESS:
		cellFrontX, cellFrontZ = camera.getFrontCellPosition(20)
		if world.getCellType(cellFrontZ, cellFrontX) == world.getObjectType("BOX"):
			world.table[cellFrontZ][cellFrontX] = world.getObjectType("NOTHING")


# Atallitjuk az eleresi utat az aktualis fajlhoz
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if not glfw.init():
	raise Exception("glfw init hiba")
	
window = glfw.create_window(1280, 720, "OpenGL window", 
	None, None)

glfw.set_window_pos(window, 0, 0)

if not window:
	glfw.terminate()
	raise Exception("glfw window init hiba")

glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
glfw.set_cursor_pos_callback(window, cursorCallback)	
glfw.set_mouse_button_callback(window, mouseButtonCallback)
glfw.make_context_current(window)
glEnable(GL_DEPTH_TEST)
glViewport(0, 0, 1280, 720)

camera = Camera(110, 0, 110)

with open("shaders/vertex_shader_texture.vert") as f:
	vertex_shader = f.read()

with open("shaders/fragment_shader_texture.frag") as f:
	fragment_shader = f.read()

shader = OpenGL.GL.shaders.compileProgram(
	OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
    OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER),
	validate=False
)


exitProgram = False

sky_choice = random.choice([1, 2])
sky_choice = 2
if sky_choice == 1:
	skyBox = SkyBox("assets/right.jpg", "assets/left.jpg", "assets/top.jpg", 
					"assets/bottom.jpg", "assets/front.jpg", "assets/back.jpg")
if sky_choice == 2:
	skyBox = SkyBox("assets/forest_posx.jpg", "assets/forest_negx.jpg", "assets/forest_posy.jpg", 
					"assets/forest_negy.jpg", "assets/forest_posz.jpg", "assets/forest_negz.jpg")

texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)

# Set the texture wrapping parameters
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
# Set texture filtering parameters
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

# load image
image = Image.open("assets/earth.jpg")
#image = image.transpose(Image.FLIP_TOP_BOTTOM)
img_data = image.convert("RGBA").tobytes()
# img_data = np.array(image.getdata(), np.uint8) # second way of getting the raw image data
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

class ObjectType(Enum):
	CUBE = 1,
	SPHERE = 2,

selectObject = ObjectType.CUBE
if selectObject == ObjectType.CUBE:
	vertices = [  0,  10,   0,  0, 1, 0, 0, 0,
	             10,  10,   0,  0, 1, 0, 0, 1,
				 10,  10, -10,  0, 1, 0, 1, 1,
				  0,  10, -10,  0, 1, 0, 1, 0,

			      0, 0,   0,  0, -1, 0, 0, 0,
				 10, 0,   0,  0, -1, 0, 0, 1,
				 10, 0, -10,  0, -1, 0, 1, 1,
				  0, 0, -10,  0, -1, 0, 1, 0,

			     10,  0,   0,  1, 0, 0, 0, 0,
				 10,  0, -10,  1, 0, 0, 0, 1,
				 10, 10, -10,  1, 0, 0, 1, 1,
				 10, 10,   0,  1, 0, 0, 1, 0,

				  0,  0,   0, -1, 0, 0, 0, 0,
				  0,  0, -10, -1, 0, 0, 0, 1,
				  0, 10, -10, -1, 0, 0, 1, 1,
				  0, 10,   0, -1, 0, 0, 1, 0,

				  0,  0,   0, 0, 0, 1, 0, 0,
				  10, 0,   0, 0, 0, 1, 0, 1,
				  10, 10,  0, 0, 0, 1, 1, 1,
				  0,  10,  0, 0, 0, 1, 1, 0,

				  0,  0,  -10,  0, 0, -1, 0, 0,
				  10, 0,  -10,  0, 0, -1, 0, 1,
				  10, 10, -10,  0, 0, -1, 1, 1,
				  0, 10, -10,   0, 0, -1, 1, 0]
	vertCount = 6*4
	shapeType = GL_QUADS
	zTranslate = -50

if selectObject == ObjectType.SPHERE:
	vertices = createSphere(10, 50, 50)
	vertCount = int(len(vertices) / 6)
	shapeType = GL_QUADS
	zTranslate = -50

vertices = numpy.array(vertices, dtype=numpy.float32)

def createObject(shader):
	glUseProgram(shader)
	vao = glGenBuffers(1)
	glBindBuffer(GL_ARRAY_BUFFER, vao)
    
	position_loc = glGetAttribLocation(shader, 'in_position')
	glEnableVertexAttribArray(position_loc)
	glVertexAttribPointer(position_loc, 3, GL_FLOAT, False, vertices.itemsize * 8, ctypes.c_void_p(0))

	normal_loc = glGetAttribLocation(shader, 'in_normal')
	glEnableVertexAttribArray(normal_loc)
	glVertexAttribPointer(normal_loc, 3, GL_FLOAT, False, vertices.itemsize * 8, ctypes.c_void_p(12))

	texture_loc = glGetAttribLocation(shader, 'in_texture')
	glEnableVertexAttribArray(texture_loc)
	glVertexAttribPointer(texture_loc, 2, GL_FLOAT, False, vertices.itemsize * 8, ctypes.c_void_p(24))


	glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
	glBindBuffer(GL_ARRAY_BUFFER, 0)

	return vao

def renderModel(vao, vertCount, shapeType):
	glBindBuffer(GL_ARRAY_BUFFER, vao)
	
	position_loc = glGetAttribLocation(shader, 'in_position')
	glEnableVertexAttribArray(position_loc)
	glVertexAttribPointer(position_loc, 3, GL_FLOAT, False, vertices.itemsize * 8, ctypes.c_void_p(0))

	glDrawArrays(shapeType, 0, vertCount)

perspMat = pyrr.matrix44.create_perspective_projection_matrix(45.0, 1280.0 / 720.0, 0.1, 100.0)

glUseProgram(shader)

lightX = -200.0
lightY = 200.0
lightZ = 100.0
lightPos_loc = glGetUniformLocation(shader, 'lightPos')
viewPos_loc = glGetUniformLocation(shader, 'viewPos')

glUniform3f(lightPos_loc, lightX, lightY, lightZ)
glUniform3f(viewPos_loc, camera.x, camera.y, camera.z )

materialAmbientColor_loc = glGetUniformLocation(shader, "materialAmbientColor")
materialDiffuseColor_loc = glGetUniformLocation(shader, "materialDiffuseColor")
materialSpecularColor_loc = glGetUniformLocation(shader, "materialSpecularColor")
materialEmissionColor_loc = glGetUniformLocation(shader, "materialEmissionColor")
materialShine_loc = glGetUniformLocation(shader, "materialShine")

lightAmbientColor_loc = glGetUniformLocation(shader, "lightAmbientColor")
lightDiffuseColor_loc = glGetUniformLocation(shader, "lightDiffuseColor")
lightSpecularColor_loc = glGetUniformLocation(shader, "lightSpecularColor")

glUniform3f(lightAmbientColor_loc, 1.0, 1.0, 1.0)
glUniform3f(lightDiffuseColor_loc, 1.0, 1.0, 1.0)
glUniform3f(lightSpecularColor_loc, 1.0, 1.0, 1.0)


class Material(Enum):
	EMERALD = 1,
	JADE = 2,
	OBSIDIAN = 3,
	PEARL = 4,
	RUBY = 5,
	TURQUOISE = 6,
	BRASS = 7,
	BRONZE = 8,
	CHROME = 9,
	COPPER = 10,
	GOLD = 11,
	SILVER = 12,
	BLACK_PLASTIC = 13,
	CYAN_PLASTIC = 14,
	GREEN_PLASTIC = 15,
	RED_PLASTIC = 16,
	WHITE_PLASTIC = 17,
	YELLOW_PLASTIC = 18,
	BLACK_RUBBER = 19,
	CYAN_RUBBER = 20,
	GREEN_RUBBER = 21,
	RED_RUBBER = 22,
	WHITE_RUBBER = 23,
	YELLOW_RUBBER = 24,

materialType = Material.YELLOW_RUBBER

if materialType is Material.EMERALD:
	glUniform3f(materialAmbientColor_loc, 0.0215, 0.1745, 0.0215)
	glUniform3f(materialDiffuseColor_loc, 0.07568, 0.61424, 0.07568)
	glUniform3f(materialSpecularColor_loc, 0.633, 0.727811, 0.633)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 76.8)

if materialType is Material.JADE:
	glUniform3f(materialAmbientColor_loc, 0.135,	0.2225,	0.1575)
	glUniform3f(materialDiffuseColor_loc, 0.54, 0.89, 0.63)
	glUniform3f(materialSpecularColor_loc, 0.316228, 0.316228, 0.316228)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 12.8)

if materialType is Material.OBSIDIAN:
	glUniform3f(materialAmbientColor_loc, 0.05375, 0.05, 0.06625)
	glUniform3f(materialDiffuseColor_loc, 0.18275, 0.17, 0.22525)
	glUniform3f(materialSpecularColor_loc, 0.332741, 0.328634, 0.346435)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 38.4)

if materialType is Material.PEARL:
	glUniform3f(materialAmbientColor_loc, 0.25, 0.20725, 0.20725)
	glUniform3f(materialDiffuseColor_loc, 1, 0.829, 0.829)
	glUniform3f(materialSpecularColor_loc, 0.296648, 0.296648, 0.296648)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 11.264)

if materialType is Material.RUBY:
	glUniform3f(materialAmbientColor_loc, 0.1745, 0.01175, 0.01175)
	glUniform3f(materialDiffuseColor_loc, 0.61424, 0.04136, 0.04136)
	glUniform3f(materialSpecularColor_loc, 0.727811, 0.626959, 0.626959)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 76.8)	

if materialType is Material.TURQUOISE:
	glUniform3f(materialAmbientColor_loc, 0.1, 0.18725, 0.1745)
	glUniform3f(materialDiffuseColor_loc, 0.396, 0.74151, 0.69102)
	glUniform3f(materialSpecularColor_loc, 0.297254, 0.30829, 0.306678)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 12.8)

if materialType is Material.BRASS:
	glUniform3f(materialAmbientColor_loc, 0.329412, 0.223529, 0.027451)
	glUniform3f(materialDiffuseColor_loc, 0.780392, 0.568627, 0.113725)
	glUniform3f(materialSpecularColor_loc, 0.992157, 0.941176, 0.807843)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 27.89743616)

if materialType is Material.BRONZE:
	glUniform3f(materialAmbientColor_loc, 0.2125, 0.1275, 0.054)
	glUniform3f(materialDiffuseColor_loc, 0.714, 0.4284, 0.18144)
	glUniform3f(materialSpecularColor_loc, 0.393548, 0.271906, 0.166721)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 25.6)

if materialType is Material.CHROME:
	glUniform3f(materialAmbientColor_loc, 0.25, 0.25, 0.25)
	glUniform3f(materialDiffuseColor_loc, 0.4, 0.4, 0.4)
	glUniform3f(materialSpecularColor_loc, 0.774597, 0.774597, 0.774597)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 76.8)

if materialType is Material.COPPER:
	glUniform3f(materialAmbientColor_loc, 0.19125, 0.0735, 0.0225)
	glUniform3f(materialDiffuseColor_loc, 0.7038, 0.27048, 0.0828)
	glUniform3f(materialSpecularColor_loc, 0.256777, 0.137622, 0.086014)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 12.8)

if materialType is Material.GOLD:
	glUniform3f(materialAmbientColor_loc, 0.24725, 0.1995, 0.0745)
	glUniform3f(materialDiffuseColor_loc, 0.75164, 0.60648, 0.22648)
	glUniform3f(materialSpecularColor_loc, 0.628281, 0.555802, 0.366065)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 51.2)	

if materialType is Material.SILVER:
	glUniform3f(materialAmbientColor_loc, 0.19225, 0.19225, 0.19225)
	glUniform3f(materialDiffuseColor_loc, 0.50754, 0.50754, 0.50754)
	glUniform3f(materialSpecularColor_loc, 0.508273, 0.508273, 0.508273)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 51.2)

if materialType is Material.BLACK_PLASTIC:
	glUniform3f(materialAmbientColor_loc, 0.0, 0.0, 0.0)
	glUniform3f(materialDiffuseColor_loc, 0.01, 0.01, 0.01)
	glUniform3f(materialSpecularColor_loc, 0.5, 0.5, 0.5)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 32)	

if materialType is Material.CYAN_PLASTIC:
	glUniform3f(materialAmbientColor_loc, 0.0, 0.1, 0.06)
	glUniform3f(materialDiffuseColor_loc, 0.00, 0.50980392, 0.50980392)
	glUniform3f(materialSpecularColor_loc, 0.50196078, 0.50196078, 0.50196078)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 32)

if materialType is Material.GREEN_PLASTIC:
	glUniform3f(materialAmbientColor_loc, 0.0, 0.0, 0.0)
	glUniform3f(materialDiffuseColor_loc, 0.1, 0.35, 0.1)
	glUniform3f(materialSpecularColor_loc, 0.45, 0.55, 0.45)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 32)

if materialType is Material.RED_PLASTIC:
	glUniform3f(materialAmbientColor_loc, 0.0, 0.0, 0.0)
	glUniform3f(materialDiffuseColor_loc, 0.5, 0.0, 0.0)
	glUniform3f(materialSpecularColor_loc, 0.7, 0.6, 0.6)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 32)

if materialType is Material.WHITE_PLASTIC:
	glUniform3f(materialAmbientColor_loc, 0.0, 0.0, 0.0)
	glUniform3f(materialDiffuseColor_loc, 0.55, 0.55, 0.55)
	glUniform3f(materialSpecularColor_loc, 0.7, 0.7, 0.7)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 32)

if materialType is Material.YELLOW_PLASTIC:
	glUniform3f(materialAmbientColor_loc, 0.0, 0.0, 0.0)
	glUniform3f(materialDiffuseColor_loc, 0.5, 0.5, 0.0)
	glUniform3f(materialSpecularColor_loc, 0.6, 0.6, 0.5)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 32)	

if materialType is Material.BLACK_RUBBER:
	glUniform3f(materialAmbientColor_loc, 0.02, 0.02, 0.02)
	glUniform3f(materialDiffuseColor_loc, 0.01, 0.01, 0.01)
	glUniform3f(materialSpecularColor_loc, 0.4, 0.4, 0.4)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 10)	

if materialType is Material.CYAN_RUBBER:
	glUniform3f(materialAmbientColor_loc, 0.0, 0.05, 0.05)
	glUniform3f(materialDiffuseColor_loc, 0.4, 0.5, 0.5)
	glUniform3f(materialSpecularColor_loc, 0.04, 0.7, 0.7)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 10)

if materialType is Material.GREEN_RUBBER:
	glUniform3f(materialAmbientColor_loc, 0.0, 0.5, 0.0)
	glUniform3f(materialDiffuseColor_loc, 0.4, 0.5, 0.4)
	glUniform3f(materialSpecularColor_loc, 0.04, 0.7, 0.04)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 10)

if materialType is Material.RED_RUBBER:
	glUniform3f(materialAmbientColor_loc, 0.05, 0.0, 0.0)
	glUniform3f(materialDiffuseColor_loc, 0.5, 0.4, 0.4)
	glUniform3f(materialSpecularColor_loc, 0.7, 0.04, 0.04)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 10)

if materialType is Material.WHITE_RUBBER:
	glUniform3f(materialAmbientColor_loc, 0.05, 0.05, 0.05)
	glUniform3f(materialDiffuseColor_loc, 0.5, 0.5, 0.5)
	glUniform3f(materialSpecularColor_loc, 0.7, 0.7, 0.7)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 10)

if materialType is Material.YELLOW_RUBBER:
	glUniform3f(materialAmbientColor_loc, 0.05, 0.05, 0.0)
	glUniform3f(materialDiffuseColor_loc, 0.5, 0.5, 0.4)
	glUniform3f(materialSpecularColor_loc, 0.7, 0.7, 0.04)
	glUniform3f(materialEmissionColor_loc, 0.0, 0.0, 0.0)
	glUniform1f(materialShine_loc, 10)	

perspectiveLocation = glGetUniformLocation(shader, "projection")
worldLocation = glGetUniformLocation(shader, "world")
viewLocation = glGetUniformLocation(shader, "view")
viewWorldLocation = glGetUniformLocation(shader, "viewWorld")

perspMat = pyrr.matrix44.create_perspective_projection_matrix(45.0, 1280.0 / 720.0, 0.1, 1000.0)
glUniformMatrix4fv(perspectiveLocation, 1, GL_FALSE, perspMat)

cube = createObject(shader)
ground = Ground(0, -10, 0, 1000, 1000)
world = Map(10, 10, 3)
world.setLightPos(lightX, lightY, lightZ)

viewMat = pyrr.matrix44.create_look_at([0.0, 0.0, 0.0], [0.0, 0.0, -1.0], [0.0, 1.0, 0.0])
angle = 0.0

elapsedTime = 0

while not glfw.window_should_close(window) and not exitProgram:
	startTime = glfw.get_time()
	glfw.poll_events()

	if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
		exitProgram = True

	directionTry = 0
	directionReal = 0
	if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
		directionTry = -30*elapsedTime*5 # beszorzom 5-tel, hogy kicsit gyorsabb legyen
		directionReal = -15*elapsedTime*5
	if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
		directionTry = 30*elapsedTime*5
		directionReal = 15*elapsedTime*5
	camera.move(directionTry)

	cellX, cellZ = camera.getCellPosition(20)

	collision = False
	if world.isSomething(cellZ, cellX) and world.getCellType(cellZ, cellX) != world.getObjectType("MONSTER"):
		collision = True 
		pass
	camera.undo()
	if not collision:
		camera.move(directionReal)

	if world.getCellType(cellZ, cellX) == world.getObjectType("MONSTER"):
		print("Meghaltál!")
		exitProgram = True

	"""
	monsterX,monsterZ = world.getMonsterCellPos()
	print(world.getCellType(monsterZ, monsterX))
	"""
	
	monsterX,monsterZ = world.getMonsterCellPos()
	monsterFrontX, monsterFrontZ = world.getMonsterFrontCells()
	#print(monsterZ, monsterX, monsterFrontZ, monsterFrontX)

	if not world.isSomething(monsterFrontZ, monsterFrontX):
		world.table[monsterFrontZ][monsterFrontX] = world.getObjectType("MONSTER")
		world.table[monsterZ][monsterX] = world.getObjectType("NOTHING")
		world.monsterCellX = monsterFrontX
		world.monsterCellZ = monsterFrontZ
	else: 
		world.monsterDirX = random.randint(-1, 1)
		world.monsterDirZ = random.randint(-1, 1)
	
	glClearDepth(1.0)
	glClearColor(0, 0.1, 0.1, 1)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

	skyBox.render(perspMat, camera.getMatrixForCubemap() )

	ground.render(camera.getMatrix(), perspMat)
	world.render(camera, perspMat)

	glUseProgram(shader)

	transMat = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, zTranslate]))
	rotMatY = pyrr.matrix44.create_from_y_rotation(math.radians(angle*0))
	rotMatX = pyrr.matrix44.create_from_x_rotation(math.radians(angle))
	rotMat = pyrr.matrix44.multiply(rotMatY, rotMatX)
	
	rotMat = pyrr.matrix44.create_from_axis_rotation(pyrr.Vector3([1., 1., 1.0]), math.radians(angle))
	
	angle += 1

	glUniform3f(viewPos_loc, camera.x, camera.y, camera.z )	

	modelMat = pyrr.matrix44.multiply(rotMat, transMat)
	glUniformMatrix4fv(worldLocation, 1, GL_FALSE, modelMat )
	glUniformMatrix4fv(viewLocation, 1, GL_FALSE, camera.getMatrix() )

	viewWorldMatrix = pyrr.matrix44.multiply(modelMat, camera.getMatrix())
	glUniformMatrix4fv(viewWorldLocation, 1, GL_FALSE, viewWorldMatrix)

	skybox_loc = glGetUniformLocation(shader, "skybox")
	glUniform1i(skybox_loc, 0)
	skyBox.activateCubeMap(shader, 1)

	glfw.swap_buffers(window)
	
	endTime = glfw.get_time()
	elapsedTime = endTime - startTime 

glfw.terminate()
