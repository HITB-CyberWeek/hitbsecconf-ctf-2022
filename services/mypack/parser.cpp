#include <vector>
#include <string>
#include <map>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define DEBUG 1
enum Types {TYPE_NIL,
            TYPE_INT,
            TYPE_UINT,
            TYPE_FLOAT,
            TYPE_DOUBLE,
            TYPE_BOOL,
            TYPE_ARRAY,
            TYPE_MAP,
            TYPE_STR,
            TYPE_BIN
};
class Element ;
struct My_pair {
    Element * el1;
    Element * el2;
};

class Element {
public:
    char type;
        unsigned int u_int;
        unsigned int s_int;
        bool logic;
        float m_float;
        double m_double;
        char *buffer;
        unsigned int buffer_len;
        My_pair  * pairs;
        Element ** list;
        int count;
    Element(int type);
    Element();
    ~Element();
    Element * TryGetKey(char * key);
    std::string toStr();
private:
    void toStr(std::string &s);
};
Element * Element::TryGetKey(char * key){
    if (this->type != TYPE_MAP){
        printf("No map %d\n",this->type);
        return 0;
    }
    for (int i=0; i<this->count; i++){
        auto el = this->pairs[i];
        if (el.el1->type == TYPE_STR || el.el1->type == TYPE_BIN ){
            if (!memcmp(el.el1->buffer,key,this->buffer_len)){
                return el.el2;
            }
        }
    }
    return 0;
}
Element::~Element(){
    printf("Destructor\n");
    if (type == TYPE_ARRAY){
        for (int i=0; i<this->count; i++){
            delete this->list[i];
        }
        delete this->list;
    }
    else if (type == TYPE_MAP){
        for (int i=0; i<this->count; i++){
            delete this->pairs[i].el1;
            delete this->pairs[i].el2;
        }
        delete this->pairs;
    }
    else if (type == TYPE_STR || type == TYPE_BIN){
        delete this->buffer;
    }
}
Element::Element(){
    this->type=type;
}

Element::Element(int type){
    this->type=type;
}

void Element::toStr(std::string &s){
#ifdef DEBUG
    printf("Type is %d\n",this->type);
#endif
    if (this->type == TYPE_ARRAY){
#ifdef DEBUG
        printf("Print array\n");
#endif
        int idx=0;
        s+="[";
        for (int i=0; i<this->count; i++){
            this->list[i]->toStr(s);
            if (idx != this->count-1)
                s+=",";
            idx+=1;
        }
        s+="]";
#ifdef DEBUG
        std::cout<<"TMP "<<s<<"\n";
#endif
    }
    else if (this->type == TYPE_MAP){
        int idx=0;
#ifdef DEBUG
        printf("Print map\n");
#endif
        s+="{";
#ifdef DEBUG
        printf("Map size:%d\n", this->count);
#endif
        for (int i=0; i<this->count; i++){
            this->pairs[i].el1->toStr(s);
            s+=":";
            this->pairs[i].el2->toStr(s);
            if (idx != this->count-1)
                s+=",";
            idx+=1;
        }
        s+="}";
#ifdef DEBUG
        std::cout<<"TMP "<<s<<"\n";
#endif
    }
    else{
        if (type == TYPE_INT){
            s+=std::to_string(this->s_int);
        }
        else if (type == TYPE_UINT){
            s+=std::to_string(this->u_int);
        }
        else if (type == TYPE_FLOAT){
            s+=std::to_string(this->m_float);
        }
        else if (type == TYPE_DOUBLE){
            s+=std::to_string(this->m_double);
        }
        else if (type == TYPE_BOOL){
            if (this->logic)
                s+="true";
            else
                s+="false";
        }
        else if (type == TYPE_NIL){
            s+="NIL";
        }
        else if (type == TYPE_STR){
            s+= std::string(this->buffer,this->buffer_len);
        }
        else if (type == TYPE_BIN){
            /*for (int i=0;i<this->buffer_len; i++){
                char c = this->buffer[i];
                s += "\\x";
                s+= (c/16 + 0x30);
                s+= (c%16 + 0x30);
            }*/
            s+=std::string(this->buffer,this->buffer_len);
//             s+=+"\"";
        }
    }
}
std::string Element::toStr(){
    std::string s;
    this->toStr(s);
    return s;
}
int ParsesAll(char * buffer, unsigned int rest_size,Element ** el){
    unsigned char type;
    int pos = 0;
    if (rest_size >= 1){
        printf("Buffer addr:%p %d %d\n",buffer,pos,buffer[pos]);
        type = buffer[pos];
    }
    else{
        return -1;
    }
#ifdef DEBUG
    printf("type: %x\n",type);
#endif
    if ((type & 0b10000000) == 0){ // 0xxxxxxx
        // positive fixint
        auto el2 = new Element(TYPE_UINT);
        int res = type & 0b1111111;
        el2->u_int = res;
#ifdef DEBUG
        printf("UINT %x\n",res);
#endif
        *el = el2;
        pos +=1;
    }
    else if ((type & 0b11100000) == 0b11100000){ // 111YYYYY
        auto el2 = new Element(TYPE_INT);
        *el = el2;
        int res = type & 0b11111;
        #ifdef DEBUG
            printf("INT %x\n",res);
        #endif
        el2->s_int = res;
        pos +=1;
    }
    else if (type == 0xCC){ // 0xcc  |ZZZZZZZZ
        if (rest_size < 2){
            return -2;
        }
        auto el2 = new Element(TYPE_UINT);
        *el = el2;
        unsigned int res = buffer[pos+1] & 0b11111111;
        #ifdef DEBUG
            printf("UINT2 %x\n",res);
        #endif
        el2->u_int = res;
        pos +=2;
    }
    else if (type == 0xCD) {//  0xcd  |ZZZZZZZZ|ZZZZZZZZ
        if (rest_size < 3){
            return -3;
        }
        auto el2 = new Element(TYPE_UINT);
        *el = el2;
        unsigned int res = (buffer[pos+1]<<8) | buffer[pos+2] ;
        #ifdef DEBUG
            printf("UINT3 %x\n",res);
        #endif
        el2->u_int = res;
        pos +=3;
    }
    else if (type == 0xCE) { // 0xce  |ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ
        if (rest_size < 5){
            return -4;
        }
        auto el2 = new Element(TYPE_UINT);
        *el = el2;
        unsigned int res = (buffer[pos+1]<<24) |(buffer[pos+2]<<16) |
                                    (buffer[pos+3]<<8) | buffer[pos+4] ;
        #ifdef DEBUG
            printf("UINT4 %x\n",res);
        #endif
        el2->u_int = res;
        pos +=5;
    }
    else if (type == 0xCF) { // 0xcf  |ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ
        if (rest_size < 9){
            return -5;
        }
        auto el2 = new Element(TYPE_UINT);
        *el = el2;
        unsigned long long int res1 = (buffer[pos+1]<<24) |(buffer[pos+2]<<16) |
                                        (buffer[pos+3]<<8) |(buffer[pos+4]);
        unsigned long long int res2 = (buffer[pos+5]<<24) |(buffer[pos+6]<<16) |
                                        (buffer[pos+7]<<8)  | buffer[pos+8] ;

        res1 = (res1 << 32 ) | res2;
        #ifdef DEBUG
            printf("UINT5 %x\n",res1);
        #endif
        el2->u_int = res1;
        pos +=9;
    }
    else if (type == 0xD0){ // 0xd0  |ZZZZZZZZ
        if (rest_size < 2){
            return -6;
        }
        auto el2 = new Element(TYPE_INT);
        *el = el2;
        char res = buffer[pos+1] & 0b11111111;
        #ifdef DEBUG
            printf("INT2 %x\n",res);
        #endif
        el2->s_int = res;
        pos +=2;
    }
    else if (type == 0xD1) {//  0xd1  |ZZZZZZZZ|ZZZZZZZZ
        if (rest_size < 3){
            return -7;
        }
        auto el2 = new Element(TYPE_INT);
        *el = el2;
        short int res = (buffer[pos+1]<<8) | buffer[pos+2] ;
        #ifdef DEBUG
            printf("INT3 %x\n",res);
        #endif
        el2->s_int = res;
        pos +=3;
    }
    else if (type == 0xD2) { // 0xd2  |ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ
        if (rest_size < 5){
            return -8;
        }
        auto el2 = new Element(TYPE_INT);
        *el = el2;

        int res = (buffer[pos+1]<<24) |(buffer[pos+2]<<16) |
                  (buffer[pos+3]<<8) | buffer[pos+4] ;
        #ifdef DEBUG
            printf("INT4 %x\n",res);
        #endif
        el2->s_int = res;
        pos +=5;
    }
    else if (type == 0xD3) { // 0xd3  |ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|ZZZZZZZZ|
        if (rest_size < 9){
            return -5;
        }
        auto el2 = new Element(TYPE_INT);
        *el = el2;
        long long int res1 = (buffer[pos+1]<<24) |(buffer[pos+2]<<16) |
                                        (buffer[pos+3]<<8) |(buffer[pos+4]);
        long long int res2 = (buffer[pos+5]<<24) |(buffer[pos+6]<<16) |
                                        (buffer[pos+7]<<8)  | buffer[pos+8] ;
        res1 = (res1 << 32 ) | res2;
        #ifdef DEBUG
            printf("INT5 %x\n",res1);
        #endif
        el2->s_int = res1;
        pos +=9;
    }
    else if (type == 0xCA) { // 0xca  |XXXXXXXX|XXXXXXXX|XXXXXXXX|XXXXXXXX
        if (rest_size < 5){
            return -6;
        }
        auto el2 = new Element(TYPE_FLOAT);
        *el = el2;
        int res1 = (buffer[pos+1]<<24) |(buffer[pos+2]<<16) |
                                        (buffer[pos+3]<<8) |(buffer[pos+4]);

        float res2 = *((float*)&res1);
        #ifdef DEBUG
            printf("FLOAT %f\n",res2);
        #endif
        el2->m_float = res2;
        pos +=5;
    }
    else if (type == 0xCB) { //  0xcb  |YYYYYYYY|YYYYYYYY|YYYYYYYY|YYYYYYYY|YYYYYYYY|YYYYYYYY|YYYYYYYY|YYYYYYYY
        if (rest_size < 9){
            return -7;
        }
        auto el2 = new Element(TYPE_DOUBLE);
        *el = el2;
        long long int res1 = (buffer[pos+1]<<24) |(buffer[pos+2]<<16) |
                                        (buffer[pos+3]<<8) |(buffer[pos+4]);
        long long int res2 = (buffer[pos+5]<<24) |(buffer[pos+6]<<16) |
                                        (buffer[pos+7]<<8)  | buffer[pos+8] ;
        res1 = (res1 << 32 ) | res2;
        double res3 = *((double*)&res1);
        #ifdef DEBUG
            printf("DOUBLE %f\n",res3);
        #endif
        el2->m_double = res3;
        pos +=5;
    }
    else if ((type & 0b11100000) == 0b10100000){ // 101XXXXX|  data
        unsigned int len = type & 0b11111;
        if (rest_size < len+1){
            return -8;
        }
        auto el2 = new Element(TYPE_STR);
        *el = el2;
        el2->buffer = new char[len+1];
        el2->buffer_len = len;
        memcpy(el2->buffer,buffer+pos+1,std::min(len,rest_size-1));
#ifdef DEBUG
        printf("Element at %p\n",el2);
        printf("String is %s(%d) %d\n",el2->buffer,el2->buffer_len,el2->type);
#endif
        pos += len+1;
    }
    else if (type == 0xd9){ // 0xd9  |YYYYYYYY|  data  |
        if (rest_size < 2){
            return -9;
        }
        unsigned int len = buffer[pos+1];          // bug
        if (rest_size < len+2){
            return -10;
        }
        auto el2 = new Element(TYPE_STR);
        *el = el2;
        el2->buffer = new char[len+1];
        el2->buffer_len = len;
        printf("LLEN %d\n",len);
        memcpy(el2->buffer,buffer+pos+2,std::min(len,rest_size-2));
        #ifdef DEBUG
//         printf("Element at %p\n",el2);
//         printf("Str buffer %p\n",el2->buffer);
//         printf("String is %s(%d) %d\n",el2->buffer,el2->buffer_len,el2->type);
        #endif
        pos += len+2;
    }
    else if (type == 0xc4){ //  0xc4  |XXXXXXXX|  data
        if (rest_size < 2){
            return -13;
        }
        unsigned int len = buffer[pos+1];          // bug
        if (rest_size < len+2){
            return -14;
        }
        auto el2 = new Element(TYPE_BIN);
        *el = el2;
        #ifdef DEBUG
        printf("Element at %p\n",el2);
        printf("Len is %d %d %d\n",len,rest_size,rest_size < len+2);
        std::cout<<len<<" "<<rest_size<<"\n";
        #endif
        el2->buffer_len = len;
        el2->buffer = new char[len+1];
        memcpy(el2->buffer,buffer+pos+2,std::min(len,rest_size-2));
        #ifdef DEBUG
        printf("DEBUG bin %p\n",el2->buffer);
        printf("BIN is %s(%d) %d\n",el2->buffer,el2->buffer_len,el2->type);
        #endif
        pos += len+2;
    }
    else if (type == 0xc5){ //  0xc5  |YYYYYYYY|YYYYYYYY|  data
        if (rest_size < 3){
            return -15;
        }
        unsigned int len = (buffer[pos+1]<<16) + buffer[pos+2];  // bug
#ifdef DEBUG
        printf("Len2 is %d %d %d\n",len,rest_size,rest_size < len+2);
        std::cout<<len<<" "<<rest_size<<"\n";
#endif
        if (rest_size < len+3){
            return -16;
        }
        auto el2 = new Element(TYPE_BIN);
        *el = el2;
        el2->buffer_len = len;
        el2->buffer = new char[len];
        memcpy(el2->buffer,buffer+pos+2,std::min(len,rest_size));
        #ifdef DEBUG
        printf("DEBUG bin %p\n",el2->buffer);
        printf("BIN2 is %s(%d) %d\n",el2->buffer,el2->buffer_len,el2->type);
        #endif
        pos += len+2;
    }
    else if ((type & 0b11110000) == 0b10010000){ // 1001XXXX|    N objects
        int len = type & 0b1111;
        auto el2 = new Element(TYPE_ARRAY);
        *el = el2;
        pos +=1;
        el2->list = new Element * [len];
        el2->count = len;
        if (rest_size-pos <1){
            delete el2;
            return -17;
        }
#ifdef DEBUG
        printf("Element at %p\n",el2);
        printf("Array of size %d\n",len);
#endif
        for (int i=0; i<len; i++){
            Element * el_res;
#ifdef DEBUG
            printf("pos:%d\n",pos);
#endif
            int new_pos = ParsesAll(buffer+pos,rest_size-pos,&el_res);
            if (new_pos<0){
                delete el2;
                return -18;
            }
            pos += new_pos;
            el2->list[i] = el_res;
            if (rest_size<pos){
                delete el2;
                return -19;
            }
        }
    }

    else if ((type & 0b11110000) == 0b10000000){ // |1000XXXX|   N*2 objects
        int len = type & 0b1111;
        auto el2 = new Element(TYPE_MAP);
        *el = el2;
        pos+=1;
        if (rest_size-pos <1){
            delete el2;
            return -20;
        }
        #ifdef DEBUG
        printf("Element at %p\n",el2);
        printf("Map of size %d\n",len);
        #endif
        el2 -> pairs = new My_pair [len];
        el2->count = len;
        for (int i=0; i<len; i++){
            Element * el_key,*el_val;
#ifdef DEBUG
            printf("pair\n");
#endif
            if (rest_size-pos <=0){
                delete el2;
                return -21;
            }
            int new_pos1 = ParsesAll(buffer+pos,rest_size-pos,&el_key);
            printf("newpos0 %d %d %d\n",new_pos1,rest_size,pos);
            pos += new_pos1;
            if (new_pos1<0){
                delete el2;
                return -22;
            }
            if (rest_size <= pos){
                delete el2;
                delete el_key;
                return -23;
            }
            int new_pos2 = ParsesAll(buffer+pos,rest_size-pos,&el_val);
            printf("newpos1 %d %d %d\n",new_pos2,rest_size,pos);
            if (new_pos2<0){
                delete el2;
                delete el_key;
                return -24;
            }
            pos += new_pos2;
            el2->pairs[i].el1 = el_key;
            el2->pairs[i].el2 = el_val;
#ifdef DEBUG
            printf("End pair\n");
#endif
        }
    }
    else{
        return -100;
    }
    return pos;
}
bool ishex(char b){
    if (b >= '0' && b <= '9')
        return true;
    if (b >= 'A' && b <= 'F')
        return true;
    if (b >= 'a' && b <= 'f')
        return true;
    return false;
}
int tohex(char b){
    if (b >= '0' && b <= '9')
        return b-'0';
    if (b >= 'A' && b <= 'F')
        return b-'A'+10;
    if (b >= 'a' && b <= 'f')
        return b-'a'+10;
    return -1;
}
char * GetBytes(char * buffer){
    int ulen = strlen(buffer);
    char *tmpbuf = new char[ulen/2];
    for (int i=0; i<ulen;i+=2){
        if (!ishex(buffer[i]) || !ishex(buffer[i+1])){
            printf("Invalid character at %d\n",i);
            continue;
        }
        int c1 = tohex(buffer[i]);
        int c2 = tohex(buffer[i+1]);
        if (c1 ==-1 || c2 == -1){
            printf("Invalid character at %d\n",i);
            continue;
        }
//         printf("c %x %x %x\n",c1,c2,((c1<<4) | c2));
        tmpbuf[i/2] = (c1<<4) | c2;
    }
    return tmpbuf;
}
void sanitize(char *buffer){
    int len = strlen(buffer);
    for (int i=0;i<len; i++){
        if (buffer[i] == '.' || buffer[i] == '\n'){
            buffer[i] = 0;
        }
    }
}
void Test1(){
    char buf[] = "\x7d";
    Element *pel;
    ParsesAll(buf,1,&pel);
    std::cout<<pel->toStr()<<"\n";
}
void Test2(){
    char buf[] = "\x93\x10\x20\x30";
    Element *pel;
    ParsesAll(buf,4,&pel);
    std::cout<<pel->toStr()<<"\n";
}
void Test3(){
    char buf[] = "\x83\x10\x20\x30\x40\x50\x60";
    Element *pel;
    ParsesAll(buf,7,&pel);
    std::cout<<pel->toStr()<<"\n";
}
void Test4(){
    char buf[] = "\x92\x83\x10\x20\x30\x40\x50\x60\x83\x10\x20\x30\x40\x50\x60";
    Element *pel;
    ParsesAll(buf,sizeof(buf),&pel);
    std::cout<<pel->toStr()<<"\n";
}
void Test5(){
    char buf[] = "0aaaaaaaaaa";
    buf[0] = '\xaa';
    Element *pel;
    ParsesAll(buf,11,&pel);
    std::cout<<pel->toStr()<<"\n";
}
void Test6(){
    char *buf = new char[65536];
    buf[0] = '\xC5';
    buf[1] = '\xFF';
    buf[2] = '\xF0';
    Element *pel;
    ParsesAll(buf,65536,&pel);
    std::cout<<pel->toStr()<<"\n";
}
//83D9026964d9083131313131313131d90e7364666173646673646661736466d90870617373776f7264d9083132333435363738
void Test7(){
    char *buf = "83D9026964d9083131313131313131d904666c6167d90e7364666173646673646661736466d90870617373776f7264d9083132333435363738";
    char * resbuf = GetBytes(buf);
    Element *pel;
    ParsesAll(resbuf ,strlen(buf)/2,&pel);
    std::cout<<pel->toStr()<<"\n";
    delete [] resbuf;
}
void Test8(){
    char *buf = "83D9026964d9083131313131313131d904666c6167d90e7364666173646673646661736466d90870617373776f7264d9083132333435363738";
    char * resbuf = GetBytes(buf);
    Element *pel;
    ParsesAll(resbuf ,strlen(buf)/2,&pel);
    printf("DEBUG ptr %p\n",pel);
    std::cout<<pel->toStr()<<"\n";

    Element *pel_2;
    ParsesAll(resbuf ,strlen(buf)/2,&pel_2);
    printf("DEBUG ptr %p\n",pel_2);
    std::cout<<pel_2->toStr()<<"\n";

    delete pel;

    Element *pel_3;
    ParsesAll(resbuf ,strlen(buf)/2,&pel_3);
    printf("DEBUG ptr %p\n",pel_3);
    std::cout<<pel_3->toStr()<<"\n";
}
#define SLOT_COUNT 10
char *myslots[SLOT_COUNT];
void Test9(){
    char *buf = "83D9026964d9083131313131313131d904666c6167d90e7364666173646673646661736466d90870617373776f7264d9083132333435363738";
    char * buf2 = "d9FFaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaad930";

    char * buf3 = "d91033333333333333333333333333333333";

    char * resbuf = GetBytes(buf);
    char * resbuf2 = GetBytes(buf2);
    char * resbuf3 = GetBytes(buf3);
    int llen = strlen(buf)/2;
    int llen2 = strlen(buf2)/2;
    int llen3 = strlen(buf3)/2;

    memset(myslots,0,SLOT_COUNT * 8);

    myslots[0] = new char[llen3];
    memcpy(myslots[0],resbuf3,llen3);
//     Element *pel_0;
//     ParsesAll(myslots[0] ,llen,&pel_0);
//     delete pel_0;

    myslots[1] = new char[llen];
    myslots[2] = new char[llen];
    myslots[3] = new char[llen2];

    memcpy(myslots[1],resbuf,llen);
    memcpy(myslots[2],resbuf,llen);
    memcpy(myslots[3],resbuf2,llen2);
    printf("%p %p %p %p\n",myslots[0],myslots[1],myslots[2],myslots[3]);
    delete myslots[0];
    delete myslots[1];
    Element *pel_3;
    ParsesAll(myslots[3],llen2,&pel_3);
    printf("DEBUG ptr %p\n",pel_3);
    std::cout<<pel_3->toStr()<<"\n";

    Element *pel_4;
    ParsesAll(myslots[2],llen,&pel_4);
    printf("DEBUG ptr %p\n",pel_4);
    std::cout<<pel_4->toStr()<<"\n";

}

/*
{
    id: "11111111",
    flag: "sdfasdfsdfasdf",
    password: "12345678"
}
83 D9 02 69 64 d9 08 31 31 31 31 31 31 31 31 d9 04 666c6167 d9 0e 7364666173646673646661736466 d9 08 70617373776f7264 d9 08 3132333435363738
m3   s2   i  d  s8    1  1  1  1  1  1  1  1
83 D9 02 69 64 d9 08 31 31 31 31 31 31 31 31 d9 04 666c6167 d9 0e 7364666173646673646661736466 d90870617373776f7264d9083132333435363738
 */

void StartProcessing(){
    char buffer[65536];
    for (int i=0; i<100; i++){
        printf("Enter command\n");
        char * res = fgets(buffer,1024,stdin);
        if (res ==0){
            printf("Finishing");
            break;
        }
        if (!strcmp(buffer,"store\n")){
            printf("Enter pack to store\n");
            char * res = fgets(buffer,1024,stdin);
            if (res ==0){
                printf("Finishing");
                break;
            }
            char * tmpbuf = GetBytes(buffer);
            int ulen = strlen(buffer)/2;
            Element *pel;
            ParsesAll(tmpbuf,ulen,&pel);
            Element * val_el = pel->TryGetKey("id");
            if (val_el==0){
                printf("No id\n");
                continue;
            }
            const char * mid = (char*)val_el->buffer;
            printf("Storing id %s\n",val_el->buffer);
            snprintf(buffer,1024,"data/%s",mid);
            sanitize(buffer);
            FILE * f1 = fopen(buffer,"rb+");
            if (f1 !=0){
                fclose(f1);
                printf("Already exists\n");
                break;
            }
            FILE * f = fopen(buffer,"wb+");
            fwrite(tmpbuf,ulen,1,f);
            fclose(f);
            delete [] tmpbuf;
            delete pel;
        }
        else if (!strcmp(buffer,"load\n")){
            printf("Enter value to load\n");
            char * res = fgets(buffer,1024,stdin);
            if (res ==0){
                printf("Finishing\n");
                break;
            }
            char buffer2[1024];
            snprintf(buffer2,1024,"data/%s",buffer);
            sanitize(buffer2);
            printf("%s",buffer2);
            FILE * f = fopen(buffer2,"rb+");
            if (!f){
                printf("No such file\n");
                break;
            }
            int nbytes = fread(buffer,1,65536,f);
            printf("%d\n",nbytes);
            if (nbytes ==0){
                printf("Empty file\n");
                break;
            }
            fclose(f);
            Element *pel;
            ParsesAll(buffer,nbytes,&pel);
            Element * val_el = pel->TryGetKey("id");
            if (val_el==0){
                printf("No id\n");
                continue;
            }
            Element * flag_el = pel->TryGetKey("flag");
            if (flag_el==0){
                printf("No flag\n");
                continue;
            }
            Element * password_el = pel->TryGetKey("password");
            if (password_el==0){
                printf("No password\n");
                continue;
            }
#ifdef DEBUG
            printf("%s %s %s \n",val_el->buffer,flag_el->buffer,password_el->buffer);
#endif
            printf("enter password\n");
            res = fgets(buffer,1024,stdin);
            sanitize(buffer);
            if (res ==0){
                printf("No password read\n");
                break;
            }
            if (strcmp(password_el->buffer,buffer)==0){
                printf("Flag is %s\n",flag_el->buffer);
            }
            else{
                printf("Invalid password\n");
            }
            delete pel;
        }
        else if (!strcmp(buffer,"search\n")){
            printf("Enter value to search\n");

        }
        else if (!strcmp(buffer,"exit\n")){
            printf("Finishing");
            break;
        }
    }
}
int main(int argc, char * argv[]){
    //Test1();
    //Test5();
    Test9();
//    StartProcessing();
    return 0;
    FILE * f = fopen(argv[1],"rb");
    if (!f){
        printf("Invalid file\n");
        return 1;
    }
    fseek(f,0,SEEK_END);
    int size = ftell(f);
    fseek(f,0,SEEK_SET);
    char * buf = new char[size];
    int res1=fread(buf,size,1,f);
    printf("res1 %d\n",res1);
    fclose(f);
    Element *pel;
    printf("Parsing %d %x %p\n",size,buf[0],buf);
    int res = ParsesAll(buf,size,&pel);
    printf("res %d\n",res);
    if (res>=0){
        std::cout<<pel->toStr()<<"\n";
        delete pel;
    }
    else{
        std::cout<<"Invalid pack\n";
    }
    delete [] buf;
    return 0;
}


