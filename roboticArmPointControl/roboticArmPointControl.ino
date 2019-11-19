//////////v2//////////
// add aim function
// modify margin function => 360-2v1
// add sequentialMovement function
// add aimCheck function
// add serialRead function

//////////v3//////////
// add r p variable
// modify initial function
// modify margin function
// modify serialRead function

//////////v4/////////
// delete aimCheck function
// add keyValue array
// add isNum function
// add isUsefulValue function
// modify serialRead function
// delete count variable


#include <Servo.h>

const double pi = 3.14159265358979;
const int firstBar = 105, secondBar = 97;
const int SERVOS = 5;
const int motor[SERVOS] = {2, 3, 9, 8, 4};
const int valueInit[SERVOS] = {90, 0, 90, 0, 0};
int value[SERVOS] = {0};
double x1, x2, y1, y2, h = 999, v, r, p;
double v1, v2;
char keyValue[] = "hvrpsimwLR";

Servo myservo[SERVOS];

void setup() {
    for(int i = 0; i < SERVOS; i++) {
        myservo[i].attach(motor[i]);
        value[i] = valueInit[i];
    }
    Serial.begin(9600);
}

void valueUp(int servo) {
    if(servo == 2) {
        if(value[servo] < 150) value[servo]++;
    } else {
        if(value[servo] < 180) value[servo]++;
    }
}

void valueDown(int servo) {
    if(value[servo] > 0) value[servo]--;
}

void value3(void) {
    value[3] = constrain(value[1] + value[2] - 90, 0, 180);
}

void servoMove(int count) {
    for(int n = 0; n < count; n++)
        for(int i = 0; i < SERVOS; i++)
            myservo[i].write(value[i]);
}

double positionX(void) {
    x1 = (double)firstBar*cos(pi/180.0*(180 - value[1]));
    x2 = (double)secondBar*cos(pi/180.0*(180 - value[1] - value[2]));
    return x1 + x2;
}

double positionY(void) {
    y1 = firstBar*sin(pi/180.0*(180 - value[1]));
    y2 = secondBar*sin(pi/180.0*(180 - value[1] - value[2]));
    return y1 + y2;
}

void positionChange(void) {// 스위치 상하좌우 기준값 이동
    if(analogRead(A3) < 300) {
        if(value[2] > 0 && (positionX() < 0 || (sqrt(h*h + v*v) < 200 && positionX() > 0))) {
            h += 1;
        }
    } else if(analogRead(A3) > 800) {
        if(value[1] > 0 && value[3] > 0 && value[2] < 150) {
            h -= 1;
        }
    }
    if(analogRead(A2) < 300) {
        if(value[2] > 0 && value[3] > 0 && sqrt(h*h + v*v) < 200) {
            v += 1;
        }
    } else if(analogRead(A2) > 800) {
        if(value[1] > 0 && v > 10 && value[3] > 0 && value[2] < 150) {
            v -= 1;
        }
    }
}

void valueChange(int benchmarkX, int benchmarkY) {// 기준값과 현재위치 비교 후 이동
    if((benchmarkX > 5 || benchmarkX < -5) || (benchmarkY > 5 || benchmarkY < 5)) {// 기계적 형태로 인한 위치 제한
        if(abs(benchmarkX - positionX()) + abs(benchmarkY - positionY()) > 2) {// 기준값과 현재위치 차이가 일정 값 이상일 경우 움직임
            double l = sqrt((double)benchmarkX/100 * benchmarkX + (double)benchmarkY/100 * benchmarkY)*10;
            double firstBarAngle = acos((firstBar*firstBar+l*l-secondBar*secondBar)/(2*firstBar*l))/pi*180;
            double secondBarAngle = acos((secondBar*secondBar+l*l-firstBar*firstBar)/(2*secondBar*l))/pi*180;
            v2 = firstBarAngle + secondBarAngle;
            if(benchmarkX < 0) {
                double angle = atan(abs(benchmarkX)/(double)benchmarkY)/pi*180;
                v1 = 90 - firstBarAngle - angle;
            } else {
                double angle = atan((double)benchmarkY/benchmarkX)/pi*180;
                v1 = 180 - firstBarAngle - angle;
            }
            if (l > 200) {
                v2 = 0;
                if (benchmarkX < 0) {
                    v1 = 90 - atan(abs(benchmarkX) / (double)benchmarkY) / pi * 180;
                }
                else {
                    v1 = 180 - atan((double)benchmarkY / benchmarkX) / pi * 180;
                }
            }
        }
    }
}

void aim() {
    if(v1 > value[1] + 1) {
        value[1]++;
    } else if(v1 < value[1] - 1) {
        value[1]--;
    }
    if(v2 > value[2] + 1) {
        valueUp(2);
    } else if(v2 < value[2] - 1) {
        value[2]--;
    }
}

void margin() {
    if(positionX() > 100 && positionY() < 50) {
        if(v1 > value[1] + 1) {
            static bool errorAreaUp = true;
            if(errorAreaUp) {
                value[2]--;
                if(value[2] < 360 - 2 * value[1] - 10) {
                    errorAreaUp = false;
                }
            } else {
                value[1]++;
                if(value[2] / 2 < 180 - value[1]) {
                    errorAreaUp = true;
                }
            }
        } else if(v1 < value[1] - 1) {
            value[1]--;
        } else {
            aim();
        }
    } else {
        aim();
    }
    if(value[0] < r - 1) {
        value[0]++;
    } else if(value[0] > r + 1) {
        value[0]--;
    }
    if(value[4] < p - 1) {
        value[4]++;
    } else if(value[4] > p + 1) {
        value[4]--;
    }
}

void rotate() {
    if(analogRead(A1) > 800) {
        if(r < 180) r++;
    } else if(analogRead(A1) < 300) {
        if(r > 0) r--;
    }
}

void picker() {
    if(analogRead(A0) > 800) {
        if(p < 90) p++;
    } else if(analogRead(A0) < 300) {
        if(p > 0) p--;
    }
}

void initial() {
    int correct = 1;
    while(correct) {
        if(value[1] > 135) valueDown(1);
        else if(value[2] < 45) valueUp(2);
        else if(value[1] > 90) valueDown(1);
        else if(value[2] < 90) valueUp(2);
        else if(value[2] > 90) valueDown(2);
        else if(value[3] > 0) valueDown(3);
        else if(value[1] > 0) valueDown(1);
        else if(value[0] < 90) valueUp(0);
        else if(value[0] > 90) valueDown(0);
        else if(value[4] > 0) valueDown(4);
        
        servoMove(50);
        correct = 0;
        for(int i = 0; i < SERVOS; i++) {
            if(value[i] != valueInit[i]) correct = 1;
        }
    }
    h = -105;
    v = 97;
    r = 90;
    p = 0;
}

void sequentialMovement() {
    static int sequence = -1;
    sequence++;
    Serial.print("  sequence = ");
    Serial.println(sequence);
    switch (sequence) {
        case 0: h = 80; v = 10; break;
        case 1: h = 200; v = 10; break;
        //case 2: p = 70; break;
        //case 3: r = 70; break;
        case 4: h = 0; v = 200; break;
        case 5: h = 0; v = 100; sequence = -1; break;
    }
}

bool isNum(char n) {
    if(n > 47 && n < 58) return true;
    else return false;
}

bool isUsefulValue(char n) {
    for(int i = 0; i < sizeof(keyValue)/sizeof(char); i++)
        if(keyValue[i] == n)
            return true;
    return false;
}

void serialRead() {
    static bool saveTemp = false;
    static int num;
    static char temp = 0, command = 0;

    if(Serial.available() > 0) {
        temp = Serial.read();
        Serial.print("  temp = ");
        Serial.println(temp);
        
        if(isUsefulValue(temp)) {
            command = temp;
            num = 0;
        } else if(isNum(temp)) {
            num *= 10;
            num += temp - 48;
        } else if(isUsefulValue(command)) {
            switch(command) {
                case 'h':
                    h = constrain(num, -100, 200);
                    break;
                case 'v':
                    v = constrain(num, 0, 200);
                    break;
                case 'r':
                    r = constrain(num, 0, 180);
                    break;
                case 'p':
                    p = constrain(num, 0, 90);
                    break;
                case 's':
                    sequentialMovement();
                    break;
                case 'i':
                    initial();
                    break;
                case 'm':
                    serialPrint();
                    break;
                case 'L':
                    if(r > 10) r -= 10;
                    break;
                case 'R':
                    if(r < 170) r += 10;
                    break;
            }
            num = 0; command = 0;
        }
    }
}

void serialPrint() {
    Serial.print("  value[0] = ");
    Serial.print(value[0]);
    Serial.print("  value[1] = ");
    Serial.print(value[1]);
    Serial.print("  value[2] = ");
    Serial.print(value[2]);
    Serial.print("  value[3] = ");
    Serial.print(value[3]);
    Serial.print("  value[4] = ");
    Serial.print(value[4]);
    Serial.print("  h = ");
    Serial.print(h);
    Serial.print("  v = ");
    Serial.print(v);
    Serial.print("  r = ");
    Serial.print(r);
    Serial.print("  p = ");
    Serial.println(p);
}

void loop() {
    if(h == 999) {
        h = positionX();
        v = positionY();
        r = valueInit[0];
        p = valueInit[4];
    }

    positionChange();
    value3();
    valueChange(h, v);
    
    margin();
    rotate();
    picker();

    if(positionX() > 50 && positionY() < 50) {
        servoMove(100);
    } else if(positionX() > 0 && positionY() < 100) {
        servoMove(50);
    } else {
        servoMove(30);
    }

    serialRead();
}
