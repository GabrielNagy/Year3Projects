#include <GL/glut.h>
#include <math.h>
#define PI 3.14159265f
GLfloat ballRadius = 0.14f;

void displayMe(void)
{
    glClear(GL_COLOR_BUFFER_BIT);
    glBegin(GL_POLYGON);
        glColor3f(1.0f, 0.0f, 0.0f);
        glVertex3f(-0.7, -0.9, 0.0);
        glVertex3f(-0.7, -0.6, 0.0);
        glVertex3f(-0.2, -0.6, 0.0);
        glVertex3f(-0.2, -0.9, 0.0);
    glEnd();
    glBegin(GL_POLYGON);
        glColor3f(1.0f, 0.0f, 0.0f);
        glVertex3f(0.7, -0.9, 0.0);
        glVertex3f(0.7, -0.6, 0.0);
        glVertex3f(0.2, -0.6, 0.0);
        glVertex3f(0.2, -0.9, 0.0);
    glEnd();
    glBegin(GL_POLYGON);
        glColor3f(1.0f, 1.0f, 0.0f);
        glVertex3f(-0.4, -0.8, 0.0);
        glVertex3f(-0.4, 0.2, 0.0);
        glVertex3f(0.4, 0.2, 0.0);
        glVertex3f(0.4, -0.8, 0.0);
    glEnd();
    glBegin(GL_POLYGON);
        glColor3f(1.0f, 0.0f, 0.0f);
        glVertex3f(-0.8, 0.2, 0.0);
        glVertex3f(0.8, 0.2, 0.0);
        glVertex3f(0.0, 0.6, 0.0);
    glEnd();
    glBegin(GL_QUADS);
        glColor3f(0.0f, 0.0f, 1.0f);
        glVertex3f(0.0, -0.1, 0.0);
        glVertex3f(0.0, 0.1, 0.0);
        glVertex3f(0.3, 0.1, 0.0);
        glVertex3f(0.3, -0.1, 0.0);
    glEnd();
    glBegin(GL_TRIANGLE_FAN);
        glColor3f(0.0f, 0.5f, 1.0f);  // Blue
        glVertex2f(-0.2f, 0.1f);       // Center of circle
        int numSegments = 100;
        GLfloat angle;
        for (int i = 0; i <= numSegments; i++) { // Last vertex same as first vertex
            angle = i * 2.0f * PI / numSegments;  // 360 deg for all segments
            glVertex2f(cos(angle) * ballRadius - 0.2, sin(angle) * ballRadius + 0.05);
        }
    glEnd();
    glBegin(GL_TRIANGLE_FAN);
        glColor3f(0.5f, 0.5f, 1.0f);  // Blue
        glVertex2f(-0.4f, -0.5f);       // Center of circle
        /* int numSegments = 100; */
        /* GLfloat angle; */
        for (int i = 0; i <= numSegments; i++) { // Last vertex same as first vertex
            angle = i * 2.0f * PI / numSegments;  // 360 deg for all segments
            glVertex2f(cos(angle) * ballRadius, sin(angle) * ballRadius - 0.3);
        }
    glEnd();
    glFlush();
}

int main(int argc, char** argv)
{
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_SINGLE);
    glutInitWindowSize(500, 500);
    glutInitWindowPosition(100, 100);
    glutCreateWindow("test window");
    glutDisplayFunc(displayMe);
    glutMainLoop();
    return 0;
}
