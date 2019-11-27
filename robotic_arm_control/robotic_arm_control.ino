#include <Servo.h>

const double pi = 3.14159265358979;
const int first_bar = 104, second_bar = 97;
const int SERVOS = 5;
const int motor[SERVOS] = {2, 3, 9, 8, 4};
const int value_init[SERVOS] = {90, 180, 90, 0, 0};

int value[SERVOS] = {0};
double x1, x2, y1, y2, h = 999, v, r, p;
double v1, v2;
char keyValue[] = "hvrpsimwLR";

Servo myservo[SERVOS];

void setup() {
    for(int i = 0; i < SERVOS; i++) {
        myservo[i].attach(motor[i]);
        value[i] = value_init[i];
    }
    Serial.begin(9600);
}

void servo_move(int count) {
    for(int n = 0; n < count; n++)
        for(int i = 0; i < SERVOS; i++)
            myservo[i].write(value[i]);
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

void setValue3(void) {
    value[3] = constrain(90 - value[1] + value[2], 0, 180);
}

double position_x(void) {
    x1 = (double)first_bar * cos(pi / 180 * value[1]);
    x2 = (double)second_bar * cos(pi / 180 * (value[1] - value[2]));
    return x1 + x2;
}

double position_y(void) {
    y1 = (double)first_bar * sin(pi / 180 * value[1]);
    y2 = (double)second_bar * sin(pi / 180 * (value[1] - value[2]));
    return y1 + y2;
}

void value_change(int benchmark_x, int benchmark_y) {
    if( abs(benchmark_x - position_x()) + abs(benchmark_y - position_y()) > 2 ) {
        double l = sqrt( (double)benchmark_x/100 * benchmark_x + (double)benchmark_y/100 * benchmark_y ) * 10;
        double first_bar_angle = acos( (first_bar * first_bar + l * l - second_bar * second_bar) / ( 2 * first_bar * l ) ) / pi * 180.0;
        double second_bar_angle = acos( (second_bar * second_bar + l * l - first_bar * first_bar ) / ( 2 * second_bar * l ) ) / pi * 180.0;
        v2 = first_bar_angle + second_bar_angle;
        if(benchmark_x < 0) {
            double angle = atan( (double)benchmark_x / benchmark_y ) / pi * 180.0;
            v1 = 90 + first_bar_angle - angle;
        } else {
            double angle = atan( (double)benchmark_y / benchmark_x ) / pi * 180.0;
            v1 = first_bar_angle + angle;
        }
        if (l > 200) {
          v2 = 0;
          if (benchmark_x < 0) {
              v1 = 90 + atan(abs(benchmark_x) / (double)benchmark_y) / pi * 180;
          } else {
              v1 = atan((double)benchmark_y/ benchmark_x) / pi * 180;
          }
        }
    }
}

void aim() {
    if(v1 > value[1] + 1) {
        valueUp(1);
    } else if(v1 < value[1] - 1) {
        valueDown(1);
    }
    if(v2 > value[2] + 1) {
        valueUp(2);
    } else if(v2 < value[2] - 1) {
        valueDown(2);
    }
}

void margin() { // typing
    if(position_x() < h) {
        if(v2 > value[2] + 1) {
            valueUp(2);
        } else if(v2 < value[2] - 1) {
            valueDown(2);
        } else {
            if(v1 > value[1] + 1) {
                valueUp(1);
            } else if(v1 < value[1] - 1) {
                valueDown(1);
            }
        }
    } else if(position_x() > h) {
        if(v1 > value[1] + 1) {
            valueUp(1);
        } else if(v1 < value[1] - 1) {
            valueDown(1);
        } else {
            if(v2 > value[2] + 1) {
                valueUp(2);
            } else if(v2 < value[2] - 1) {
                valueDown(2);
            }
        }
    } else {
        aim();
    }
    if(value[0] < r) {
        valueUp(0);
    } else if(value[0] > r) {
        valueDown(0);
    }
    if(value[4] < p) {
        valueUp(4);
    } else if(value[4] > p) {
        valueDown(4);
    }
}

void initial() {
    bool init_a = true, init_b = true;
    while(init_a) {
        if(value[4] > 0) valueDown(4);
        else if(value[3] < 180) valueUp(3);
        else if(value[1] < 30) valueUp(1);
        else if(value[2] < 30) valueUp(2);
        else if(value[1] < 60) valueUp(1);
        else if(value[2] < 60) valueUp(2);
        else if(value[1] < 90) valueUp(1);
        else if(value[2] < 90) valueUp(2);
        else init_a = false;
        servo_move(100);
    }
    while(init_b) {
        if(value[2] > 90) valueDown(2);
        else if(value[1] < 180) valueUp(1);
        else if(value[3] > 0) valueDown(3);
        else if(value[0] < 90) valueUp(0);
        else if(value[0] > 90) valueDown(0);
        else init_b = false;
        servo_move(100);
    }
    h = -104;
    v = 97;
    r = 90;
    p = 0;
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
    static bool negative = false;

    if(Serial.available() > 0) {
        temp = Serial.read();
        Serial.print("  temp = ");
        Serial.println(temp);
        
        if(isUsefulValue(temp)) {
            command = temp;
            num = 0;
        } else if (temp == 45) {
            negative = true;
        } else if(isNum(temp)) {
            num *= 10;
            num += temp - 48;
        } else if(isUsefulValue(command)) {
            switch(command) {
                case 'h':
                    if(negative)
                        num *= -1;
                    h = constrain(num, -120, 200);
                    break;
                case 'v':
                    if(negative)
                        num += -1;
                    v = constrain(num, -50, 200);
                    break;
                case 'r':
                    r = constrain(num, 0, 180);
                    break;
                case 'p':
                    p = constrain(num, 0, 90);
                    break;
                case 'i':
                    initial();
                    break;
                case 'm':
                    serialPrint();
                    break;
                case 'L':
                    if(r > 0) r--;
                    break;
                case 'R':
                    if(r < 180) r++;
                    break;
            }
            num = 0; command = 0; negative = false;
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
    Serial.print("  v1 = ");
    Serial.print(v1);
    Serial.print("  v2 = ");
    Serial.print(v2);
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
        h = position_x();
        v = position_y();
        r = value_init[0];
        p = value_init[4];
    }

    setValue3();
    value_change(h, v);

    margin();

    if(position_x() > 50 && position_y < 50) {
        servo_move(100);
    } else if(position_x() > 0 && position_y < 100) {
        servo_move(80);
    } else {
        servo_move(50);
    }
    
    serialRead();
}
