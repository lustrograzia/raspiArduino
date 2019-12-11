#include <Servo.h>

const double pi = 3.14159265358979;
const int first_bar = 105, second_bar = 100;  // 로봇 팔 길이 설정
const int SERVOS = 5; // 서보모터 개수
const int motor[SERVOS] = {2, 3, 9, 8, 4};  // 서보모터 사용 핀
const int value_init[SERVOS] = {90, 180, 100, 0, 0};  // 서보모터 각도 초기화

int value[SERVOS] = {0};  // 모터 각도 출력 배열
double x1, x2, y1, y2;  // 두번째 세번째 관절 도달 위치
double v1, v2;  // 위치로 계산한 첫번째 두번째 관절의 모터 각도
double h, v, r, p, n; // 수평 위치, 수직 위치, 좌우 회전 각도, 집게 각도, 세번째 관절 각도

bool pick_sequence = false; // pick_object 함수 동작 유무 설정 변수
bool move_confirm = false;  // move_ready 함수 동작 유무 설정 변수

Servo myservo[SERVOS];  // 서보모터 선언

void setup() {
    for(int i = 0; i < SERVOS; i++) {
        myservo[i].attach(motor[i]);  // 서모모터 해당핀 사용 선언
        value[i] = value_init[i];     // 초기값 출력 배열에 입력
    }
    Serial.begin(115200);

    h = position_x(); // 초기 수평 위치
    v = position_y(); // 초기 수직 위치
    r = value_init[0];  // 초기 좌우 회전 각도
    p = value_init[4];  // 초기 집게 각도
    n = 10;   // 초기 세번째 관절(집게가 달린 관절) 각도
}

void servo_move(int count) {    // 서보모터에 값을 출력하는 함수
    for(int n = 0; n < count; n++)  // 입력받은 횟수만큼 반복하여 출력하는 것으로
        for(int i = 0; i < SERVOS; i++)   // 모터의 회전속도 조절
            myservo[i].write(value[i]);   // 출력 배열 값을 해당 모터에 출력
}

void valueUp(int servo) {   // 해당 모터의 각도 값 1씩 증가
    if(servo == 2) {
        if(value[servo] < 150) value[servo]++;    // 두번째 관절의 각도 150까지로 제한
    } else {
        if(value[servo] < 180) value[servo]++;    // 나머지 각도 180까지로 제한
    }
}

void valueDown(int servo) {   // 해당 모터의 각도 값 1씩 감소
    if(value[servo] > 0) value[servo]--;    // 0까지로 제한
}

void setValue3(int set_n=10) {  // 입력 값만큼 세번째 관절(집게 달린 관절)의 각도 계산
                                // 첫번째 두번째 각도에 따라 계산하여
                                // 입력 값의 수평으로부터 각도 유지
    value[3] = constrain(90 - value[1] + value[2] - set_n, 0, 180);
}

double position_x(void) {   // 현재 수평 위치 계산
    x1 = (double)first_bar * cos(pi / 180 * value[1]);  // 두번째 관절의 수평 변위
    x2 = (double)second_bar * cos(pi / 180 * (value[1] - value[2]));  // 세번째 관절의 수평 변위
    return x1 + x2; // 두 변위의 합으로 수평위치 계산
}

double position_y(void) {   // 현재 수직 위치 계산
    y1 = (double)first_bar * sin(pi / 180 * value[1]);  // 두번째 관절의 수직 변위
    y2 = (double)second_bar * sin(pi / 180 * (value[1] - value[2]));  // 세번째 관절의 수직 변위
    return y1 + y2; // 두 변위의 합으로 수직위치 계산
}

void value_change(int benchmark_x, int benchmark_y) { // 입력받은 수평, 수직 위치값에 따른 첫번째 두번째 관절의 각도 계산
    if( abs(benchmark_x - position_x()) + abs(benchmark_y - position_y()) > 2 ) {   // 현재 위치와 입력받은 위치의 거리가 2이상일 경우
        // 제2코사인 법칙을 사용하여 각도를 계산
        double l = sqrt( (double)benchmark_x/100 * benchmark_x + (double)benchmark_y/100 * benchmark_y ) * 10;
        double first_bar_angle = acos( (first_bar * first_bar + l * l - second_bar * second_bar) / ( 2 * first_bar * l ) ) / pi * 180.0;
        double second_bar_angle = acos( (second_bar * second_bar + l * l - first_bar * first_bar ) / ( 2 * second_bar * l ) ) / pi * 180.0;
        v2 = int(first_bar_angle + second_bar_angle);   // 두번째 관절 각도
        if(benchmark_x < 0) { // 수평 위치가 0보다 작을 때
            double angle = atan( (double)benchmark_x / benchmark_y ) / pi * 180.0;
            v1 = int(90 + first_bar_angle - angle);
        } else {  // 수평 위치가 0보다 클 때
            double angle = atan( (double)benchmark_y / benchmark_x ) / pi * 180.0;
            v1 = int(first_bar_angle + angle);
        }
        if (l > 200) {  // 로봇팔 최대길이 이상일 경우
          v2 = 0; // 두번째 각도 최대로 첫번째 각도로만 조절
          if (benchmark_x < 0) {  // 첫번째 관절 각도 조절, 수평 위치가 0보다 작을 때
              v1 = int(90 + atan(abs(benchmark_x) / (double)benchmark_y) / pi * 180);
          } else {    // 수평 위치가 0보다 클 때
              v1 = int(atan((double)benchmark_y/ benchmark_x) / pi * 180);
          }
        }
    }
}

void aim() {  // 계산한 v1 v2 값에 현재 각도 value를 맞추는 함수
    if(v1 > value[1]) {
        valueUp(1);
    } else if(v1 < value[1]) {
        valueDown(1);
    }
    if(v2 > value[2]) {
        valueUp(2);
    } else if(v2 < value[2]) {
        valueDown(2);
    }
}

void margin() { // 수평 이동 시 첫번째 각도와 두번째 각도가 같이 변함에도 불구하고
                // 하드웨어는 둘 중 한쪽이 먼저 변함으로 인해 바닥에 부딪히는 현상을
                // 개선하기 위해 이동 방향에 따라 나눠서 동작
    if(position_x() < h) {  // 바깥쪽으로 움직일 때
        if(v2 > value[2]) {   // 두번째 관절 먼저 동작 후
            valueUp(2);
        } else if(v2 < value[2]) {
            valueDown(2);
        } else {              // 첫번째 관절 동작
            if(v1 > value[1]) {
                valueUp(1);
            } else if(v1 < value[1]) {
                valueDown(1);
            }
        }
    } else if(position_x() > h) { // 안쪽으로 움직일 때
        if(v1 > value[1]) {   // 첫번째 관절 동작 후
            valueUp(1);
        } else if(v1 < value[1]) {
            valueDown(1);
        } else {              // 두번째 관절 동작
            if(v2 > value[2]) {
                valueUp(2);
            } else if(v2 < value[2]) {
                valueDown(2);
            }
        }
    } else {  // 이외에는 무관
        aim();
    }
    if(value[0] < r) {    // 좌우 회전 각도 일치
        valueUp(0);
    } else if(value[0] > r) {
        valueDown(0);
    }
    if(value[4] < p) {    // 집게 각도 일치
        valueUp(4);
    } else if(value[4] > p) {
        valueDown(4);
    }
}

void initial() {  // 초기화
    bool init_a = true, init_b = true;
    while(init_a) {
        if((abs(position_x() - h) < 2) && (abs(position_y() - v) < 2)
            && value[0] == r && value[4] == p)
        {
            if(h > 100)
                h = 100;
            else if(v < 50)
                v = 50;
            else if(h > 0 || v < 100) {
                h = 0;
                v = 100;
            } else
              init_a = false;
        }
        margin();
    }
    /*
    while(init_a) {
        if(value[4] > 0) valueDown(4);
        else if(value[3] < 180) valueUp(3);
        else if(value[2] < 30) valueUp(2);
        else if(value[1] < 30) valueUp(1);
        else if(value[2] < 90) valueUp(2);
        else if(value[2] > 90) valueDown(2);
        else if(value[1] < 90) valueUp(1);
        else init_a = false;
        servo_move(100);
    }
    while(init_b) {
        if(value[3] > 90) valueDown(3);
        else if(value[1] < 170) valueUp(1);
        else if(value[3] > 0) valueDown(3);
        else if(value[2] < 100) valueUp(2);
        else if(value[1] < 180) valueUp(1);
        else init_b = false;
        servo_move(100);
    }*/
    h = position_x();
    v = position_y();
    r = value_init[0];
    p = value_init[4];
    n = 10;
}

bool isNum(char c) {  // 입력 값이 숫자인지 판단
    if(c > 47 && c < 58) return true;
    else return false;
}

void serial_read() {  // 시리얼 통신으로 입력된 값이 따른 동작 함수
    static String command = "hvrpnmis"; // 동작 명령어
    if(Serial.available() > 0) {  // 시리얼 통신으로 입력받은 값이 있을 경우
        String inString = Serial.readStringUntil('\n'); // 개행문자가 나올 때까지 string으로 입력
        //Serial.println(inString);

        char c; // 명령어를 저장할 변수
        String str_num = "";  // 숫자를 저장할 변수
        for(int i = 0; i < inString.length(); i++) {  // 각 문자 판단
            if(command.indexOf(inString[i] != -1)) {  // 해당 문자가 command 값이라면
                if(inString[i] == 'i') {  // i이면 초기화
                    initial();
                } else if(inString[i] == 'm') { // m이면 현재 값 출력
                    serial_print();
                } else if(inString[i] == 's') { // s이면 pick_object 동작
                    pick_sequence = true;
                } else {  // ims를 제외한 명령어라면
                    c = inString[i];  // 명령어를 c에 저장
                    for(int j = i + 1; j < inString.length(); j++) {  // 명령어 뒤의 숫자값 추출
                        if(inString[j] == 45 || isNum(inString[j])) { // -값 또는 숫자값이면
                            str_num += inString[j]; // 숫자 저장 변수에 추가
                        } else {  // - 또는 숫자가 아니면
                            i = j - 1;  // command인지 판단 위치로 돌아감
                            break;
                        }
                    }
                    if(str_num != "")   // 명령어 뒤 숫자값이 있으면
                        input_value(c, str_num.toInt());  // 해당 명령어 실행
                                                          // 명령어와 숫자값 int로 변환하여 입력
                    str_num = ""; // 숫자 변수 초기화
                }
            }
        }
    }
}

void pick_object(){   // 물체를 잡을 위치에 도달했을 시 정해진대로 동작 sequence 수행
    static int sequence = 1;
    switch(sequence) {
        case 1:
            p = 75;   // 집게 각도 75
            if(value[4] == p)
                sequence++;
            break;
        case 2:
            v = 50; h = 100;    // 수직 50 수평 100
            if(abs(position_y() - v) < 5 && abs(position_x() - h) < 5)
                sequence++;   // 어느정도 도달하면 다음 단계로 이동
            break;
        case 3:
            r = 170;    // 회전 170
            if(value[0] == r)
                sequence++;
            break;
        case 4:
            v = -40;    // 수직 -40
            if(abs(position_y() - v) < 5)
                sequence++;
            break;
        case 5:
            p = 0;    // 집게 0
            if(value[4] == p)
                sequence++;
            break;
        case 6:
            v = 50;   // 수직 50
            if(abs(position_y() - v) < 5)
                sequence++;
            break;
        case 7:
            r = 90; v = 53; h = 90;   // 회전 90 수직 53 수평 90
            if(v1 == value[1] && v2 == value[2])
                sequence++;
            break;
        case 8:
            initial();    // 위치 초기화
            sequence = 1;
            pick_sequence = false;
            break;
    }
}

void input_value(char command, int num) {   // 해당 값으로 변환
    move_confirm = true;  // 동작을 명령했으므로 해당 값에 도달 여부 확인 함수 활성화
    switch(command) {
        case 'h':
            h = constrain(num, -120, 200);  // 수평값 -120 ~ 200 제한
            break;
        case 'v':
            v = constrain(num, -50, 200);   // 수직값 -50 ~ 200 제한
            break;
        case 'r':
            r = constrain(num, 0, 180);   // 좌우 회전 0 ~ 180 제한
            break;
        case 'p':
            p = constrain(num, 0, 90);    // 집게 0 ~ 90 제한
            break;
        case 'n':
            n = constrain(num, 0, 180);   // 집게 관절 0 ~ 180 제한
            break;
    }
}

void serial_print() {   // 현재 값 출력
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
    Serial.print("  v3 = ");
    Serial.print(90 - value[1] + value[2]);
    Serial.print("  h = ");
    Serial.print(h);
    Serial.print("  v = ");
    Serial.print(v);
    Serial.print("  r = ");
    Serial.print(r);
    Serial.print("  p = ");
    Serial.print(p);
    Serial.print("  n = ");
    Serial.print(n);
    Serial.print("  h = ");
    Serial.println(int(position_x()));
}

void move_ready() {   // 이동할 위치를 입력받아 계산된 값에 도달 여부를 확인 후
    if(v1 == value[1] && v2 == value[2] && r == value[0]) { // 도달했다면
        Serial.println("y");    // y를 출력
        move_confirm = false;    // 확인 함수 비활성화
    }
}

void loop() {
    if(pick_sequence)   // 집을 위치에 도달 여부 확인
        pick_object();
    if(move_confirm)    // 입력된 위치 도달 여부 확인
        move_ready();
        
    setValue3(n);       // 세번째 관절 각도 계산
    value_change(h, v); // 입력된 위치에 따른 각도 계산

    margin();           // 입력된 위치로 이동

    if(pick_sequence) {   // 위치에 따른 이동 속도 설정
        servo_move(120);
    } else if(position_x() > 50 && position_y() < 50) {
        servo_move(200);
    } else if(position_x() > 0 && position_y() < 100) {
        servo_move(150);
    } else {
        servo_move(100);
    }
    
    serial_read();      // 명령어 입력 확인
}
