#include<GL/gl.h>
#include<GL/glut.h>
#include<stdio.h>


GLuint object;
float objectrot;
char ch='1';

void loadObj(char *fname)
{
  FILE *fp;
  int read;
  GLfloat x, y, z;
  char ch;
  object=glGenLists(1);
  fp=fopen(fname,"r");
  if (!fp) 
    {
      printf("can't open file %s\n", fname);
      exit(1);
    }
  glPointSize(2.0);
  glNewList(object, GL_COMPILE);
  {
    glPushMatrix();
    glBegin(GL_POINTS);
    while(!(feof(fp)))
      {
        read=fscanf(fp,"%c %f %f %f",&ch,&x,&y,&z);
        if(read==4&&ch=='v')
          {
            glVertex3f(x,y,z);
          }
      }
    glEnd();
  }
  glPopMatrix();
  glEndList();
  fclose(fp);
}


void reshape(int w, int h)
{    
  glViewport(0,0,w,h);
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  gluPerspective (60, (GLfloat)w / (GLfloat)h, 0.1, 1000.0);
  //glOrtho(-25,25,-2,2,0.1,100);	
  glMatrixMode(GL_MODELVIEW);
}

void drawObject()
{
  glPushMatrix();
  glTranslatef(0,-40.00,-105);
  glColor3f(1.0,0.23,0.27);
  glScalef(1,1,1);
  glRotatef(objectrot,0,1,0);
  glCallList(object);
  glPopMatrix();
  objectrot=objectrot+0.6;
  if(objectrot>360)objectrot=objectrot-360;
}

void initializeLight()
{
  glClearColor(0.0, 0.0, 0.0, 0.0);
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0);

  // set up lighting
  glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE);
  glEnable(GL_LIGHTING);
  glEnable(GL_LIGHT0);

  // set lighting intensity and color
  GLfloat ambientLight[] = {1.0, 1.0, 1.0, 1.0};
  GLfloat diffuseLight[] = {0.8, 0.8, 0.5, 0.8};
  GLfloat specularLight[] = {1.0, 1.0, 1.0, 1.0};
  glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLight);
  glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLight);
  glLightfv(GL_LIGHT0, GL_SPECULAR, specularLight);

  // set light position
  GLfloat lightPosition[] = {1, 1, 0.0, 1.0};
  glLightfv(GL_LIGHT0, GL_POSITION, lightPosition);
}

void display(void)
{  
  glClearColor (0.0,0.0,0.0,1.0); 
  glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  glLoadIdentity();
  drawObject();
  glutSwapBuffers();

}

int main(int argc,char **argv)
{
  glutInit(&argc,argv);
  glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH);
  glutInitWindowSize(800,450);
  glutInitWindowPosition(20,20);
  glutCreateWindow("ObjLoader");
  glutReshapeFunc(reshape);
  glutDisplayFunc(display);
  glutIdleFunc(display);
  loadObj("obj/cap.obj");
  initializeLight();
  glutMainLoop();
  return 0;
}
