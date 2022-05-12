#ifndef DHRYLOAD_H
#define DHRYLOAD_H


#include "config.h"


// *****************************************************************************
// Type definitions from original file "dhry.h"

// measurements should last at least about 2 seconds
#define Too_Small_Time 2000000

typedef enum { Ident_1, Ident_2, Ident_3, Ident_4, Ident_5 } Enumeration;

typedef int  One_Thirty;
typedef int  One_Fifty;
typedef char Capital_Letter;
typedef int  Boolean;
typedef char Str_30[31];
typedef int  Arr_1_Dim[25];        // <-- changed from 50
typedef int  Arr_2_Dim[25][25];    // <-- changed from 50

typedef struct record {
    struct record* Ptr_Comp;
    Enumeration    Discr;
    union {
        struct {
            Enumeration Enum_Comp;
            int         Int_Comp;
            char        Str_Comp[31];
        } var_1;
        struct {
            Enumeration E_Comp_2;
            char        Str_2_Comp[31];
        } var_2;
        struct {
            char Ch_1_Comp;
            char Ch_2_Comp;
        } var_3;
    } variant;
} Rec_Type, *Rec_Pointer;


// *****************************************************************************
// Global variables from original file "dhry_1.c"

Rec_Pointer Ptr_Glob;
Rec_Pointer Next_Ptr_Glob;
Boolean     Bool_Glob;
char        Ch_1_Glob;
char        Ch_2_Glob;
int         Int_Glob;
int         Arr_1_Glob[25];        // <-- changed from 50
int         Arr_2_Glob[25][25];    // <-- changed from 50

long   Begin_Time;
long   End_Time;
long   User_Time;
double Microseconds;
double Dhrystones_Per_Second;
double Vax_Mips;


// *****************************************************************************
// Forward declarations for all dhrystone functions
// from original files "dhry_1.c" and "dhry_2.c"

void Proc_1(Rec_Pointer Ptr_Val_Par);
void Proc_2(One_Fifty* Int_Par_Ref);
void Proc_3(Rec_Pointer* Ptr_Ref_Par);
void Proc_4();
void Proc_5();
void Proc_6(Enumeration Enum_Val_Par, Enumeration* Enum_Ref_Par);
void Proc_7(One_Fifty  Int_1_Par_Val,
            One_Fifty  Int_2_Par_Val,
            One_Fifty* Int_Par_Ref);
void Proc_8(Arr_1_Dim Arr_1_Par_Ref,
            Arr_2_Dim Arr_2_Par_Ref,
            int       Int_1_Par_Val,
            int       Int_2_Par_Val);

Enumeration Func_1(Capital_Letter Ch_1_Par_Val, Capital_Letter Ch_2_Par_Val);
Boolean     Func_2(Str_30 Str_1_Par_Ref, Str_30 Str_2_Par_Ref);
Boolean     Func_3(Enumeration Enum_Par_Val);


// *****************************************************************************
// Dhrystone functions from original files "dhry_1.c" and "dhry_2.c"

void Proc_1(Rec_Pointer Ptr_Val_Par) {
    Rec_Pointer Next_Record = Ptr_Val_Par->Ptr_Comp;

    *Ptr_Val_Par->Ptr_Comp = *Ptr_Glob;

    Ptr_Val_Par->variant.var_1.Int_Comp = 5;

    Next_Record->variant.var_1.Int_Comp = Ptr_Val_Par->variant.var_1.Int_Comp;
    Next_Record->Ptr_Comp               = Ptr_Val_Par->Ptr_Comp;

    Proc_3(&Next_Record->Ptr_Comp);

    if (Next_Record->Discr == Ident_1) {
        Next_Record->variant.var_1.Int_Comp = 6;
        Proc_6(Ptr_Val_Par->variant.var_1.Enum_Comp,
               &Next_Record->variant.var_1.Enum_Comp);
        Next_Record->Ptr_Comp = Ptr_Glob->Ptr_Comp;
        Proc_7(Next_Record->variant.var_1.Int_Comp,
               10,
               &Next_Record->variant.var_1.Int_Comp);
    } else {
        *Ptr_Val_Par = *Ptr_Val_Par->Ptr_Comp;
    }
}


void Proc_2(One_Fifty* Int_Par_Ref) {
    One_Fifty   Int_Loc = *Int_Par_Ref + 10;
    Enumeration Enum_Loc;

    do {
        if (Ch_1_Glob == 'A') {
            Int_Loc -= 1;
            Enum_Loc = Ident_1;

            *Int_Par_Ref = Int_Loc - Int_Glob;
        }
    } while (Enum_Loc != Ident_1);
}


void Proc_3(Rec_Pointer* Ptr_Ref_Par) {
    if (Ptr_Glob != NULL) {
        *Ptr_Ref_Par = Ptr_Glob->Ptr_Comp;
    }

    Proc_7(10, Int_Glob, &Ptr_Glob->variant.var_1.Int_Comp);
}


void Proc_4() {
    Boolean Bool_Loc = Ch_1_Glob == 'A';

    Bool_Glob = Bool_Loc | Bool_Glob;
    Ch_2_Glob = 'B';
}


void Proc_5() {
    Ch_1_Glob = 'A';
    Bool_Glob = false;
}


void Proc_6(Enumeration Enum_Val_Par, Enumeration* Enum_Ref_Par) {
    *Enum_Ref_Par = Enum_Val_Par;

    if (!Func_3(Enum_Val_Par)) {
        *Enum_Ref_Par = Ident_4;
    }

    switch (Enum_Val_Par) {
        case Ident_1:
            *Enum_Ref_Par = Ident_1;
            break;
        case Ident_2:
            if (Int_Glob > 100)
                *Enum_Ref_Par = Ident_1;
            else
                *Enum_Ref_Par = Ident_4;
            break;
        case Ident_3:
            *Enum_Ref_Par = Ident_2;
            break;
        case Ident_4:
            break;
        case Ident_5:
            *Enum_Ref_Par = Ident_3;
            break;
    }
}


void Proc_7(One_Fifty  Int_1_Par_Val,
            One_Fifty  Int_2_Par_Val,
            One_Fifty* Int_Par_Ref) {
    One_Fifty Int_Loc = Int_1_Par_Val + 2;
    *Int_Par_Ref      = Int_2_Par_Val + Int_Loc;
}


void Proc_8(Arr_1_Dim Arr_1_Par_Ref,
            Arr_2_Dim Arr_2_Par_Ref,
            int       Int_1_Par_Val,
            int       Int_2_Par_Val) {
    One_Fifty Int_Index;
    One_Fifty Int_Loc = Int_1_Par_Val + 5;

    Arr_1_Par_Ref[Int_Loc]      = Int_2_Par_Val;
    Arr_1_Par_Ref[Int_Loc + 1]  = Arr_1_Par_Ref[Int_Loc];
    Arr_1_Par_Ref[Int_Loc + 15] = Int_Loc;

    for (Int_Index = Int_Loc; Int_Index <= Int_Loc + 1; ++Int_Index) {
        Arr_2_Par_Ref[Int_Loc][Int_Index] = Int_Loc;
    }

    Arr_2_Par_Ref[Int_Loc][Int_Loc - 1] += 1;
    Arr_2_Par_Ref[Int_Loc + 10][Int_Loc] = Arr_1_Par_Ref[Int_Loc];

    Int_Glob = 5;
}


Enumeration Func_1(Capital_Letter Ch_1_Par_Val, Capital_Letter Ch_2_Par_Val) {
    Capital_Letter Ch_1_Loc = Ch_1_Par_Val;
    Capital_Letter Ch_2_Loc = Ch_1_Loc;

    if (Ch_2_Loc != Ch_2_Par_Val) {
        return Ident_1;
    } else {
        Ch_1_Glob = Ch_1_Loc;
        return Ident_2;
    }
}


Boolean Func_2(Str_30 Str_1_Par_Ref, Str_30 Str_2_Par_Ref) {
    Capital_Letter Ch_Loc;
    One_Thirty     Int_Loc = 2;

    while (Int_Loc <= 2) {
        if (Func_1(Str_1_Par_Ref[Int_Loc], Str_2_Par_Ref[Int_Loc + 1])
            == Ident_1) {
            Ch_Loc = 'A';
            Int_Loc += 1;
        }
    }

    if (Ch_Loc >= 'W' && Ch_Loc < 'Z') {
        Int_Loc = 7;
    }

    if (Ch_Loc == 'R') {
        return true;
    } else {
        if (strcmp(Str_1_Par_Ref, Str_2_Par_Ref) > 0) {
            Int_Loc += 7;
            Int_Glob = Int_Loc;
            return true;
        } else {
            return false;
        }
    }
}


Boolean Func_3(Enumeration Enum_Par_Val) {
    Enumeration Enum_Loc = Enum_Par_Val;

    if (Enum_Loc == Ident_3)
        return true;
    else
        return false;
}


// *****************************************************************************
// Modified version of the main() function from original file "dhry_1.c"

void dhryload() {
    One_Fifty   Int_1_Loc;
    One_Fifty   Int_2_Loc;
    One_Fifty   Int_3_Loc;
    Enumeration Enum_Loc;
    Str_30      Str_1_Loc;
    Str_30      Str_2_Loc;
    char        Ch_Index;
    long        Run_Index;         // <-- changed from int
    long        Number_Of_Runs;    // <-- changed from int

    Number_Of_Runs = 750000;

    Next_Ptr_Glob = (Rec_Pointer) malloc(sizeof(Rec_Type));
    Ptr_Glob      = (Rec_Pointer) malloc(sizeof(Rec_Type));

    Ptr_Glob->Ptr_Comp                = Next_Ptr_Glob;
    Ptr_Glob->Discr                   = Ident_1;
    Ptr_Glob->variant.var_1.Enum_Comp = Ident_3;
    Ptr_Glob->variant.var_1.Int_Comp  = 40;

    strcpy(Ptr_Glob->variant.var_1.Str_Comp, "DHRYSTONE PROGRAM, SOME STRING");
    strcpy(Str_1_Loc, "DHRYSTONE PROGRAM, 1'ST STRING");

    Arr_2_Glob[8][7] = 10;

#if SERIAL_MONITOR
    Serial.println("Dhrystone Benchmark, Version 2.1 (Language: C)");
    Serial.print("Execution starts, ");
    Serial.print(Number_Of_Runs);
    Serial.println(" runs through Dhrystone");
    Serial.println();
#endif


    // start timer
    Begin_Time = micros();

    for (Run_Index = 1; Run_Index <= Number_Of_Runs; ++Run_Index) {
        Proc_5();
        Proc_4();

        Int_1_Loc = 2;
        Int_2_Loc = 3;
        strcpy(Str_2_Loc, "DHRYSTONE PROGRAM, 2'ND STRING");
        Enum_Loc  = Ident_2;
        Bool_Glob = !Func_2(Str_1_Loc, Str_2_Loc);

        while (Int_1_Loc < Int_2_Loc) {
            Int_3_Loc = 5 * Int_1_Loc - Int_2_Loc;
            Proc_7(Int_1_Loc, Int_2_Loc, &Int_3_Loc);
            Int_1_Loc += 1;
        }

        Proc_8(Arr_1_Glob, Arr_2_Glob, Int_1_Loc, Int_3_Loc);
        Proc_1(Ptr_Glob);

        for (Ch_Index = 'A'; Ch_Index <= Ch_2_Glob; ++Ch_Index) {
            if (Enum_Loc == Func_1(Ch_Index, 'C')) {
                Proc_6(Ident_1, &Enum_Loc);
                strcpy(Str_2_Loc, "DHRYSTONE PROGRAM, 3'RD STRING");
                Int_2_Loc = Run_Index;
                Int_Glob  = Run_Index;
            }
        }

        Int_2_Loc = Int_2_Loc * Int_1_Loc;
        Int_1_Loc = Int_2_Loc / Int_3_Loc;
        Int_2_Loc = 7 * (Int_2_Loc - Int_3_Loc) - Int_1_Loc;
        Proc_2(&Int_1_Loc);
    }

    // stop timer
    End_Time = micros();

#if SERIAL_MONITOR
    Serial.println("Execution ends");
#endif

    User_Time = End_Time - Begin_Time;

    if (User_Time < Too_Small_Time) {
#if SERIAL_MONITOR
        Serial.println("Measured time too small to obtain meaningful results");
        Serial.println("Please increase number of runs");
        Serial.println();
#endif
    } else {
        Microseconds = (double) User_Time / (double) Number_Of_Runs;
        Dhrystones_Per_Second =
            (double) Number_Of_Runs / ((double) User_Time / 1000000.0);
        Vax_Mips = Dhrystones_Per_Second / 1757.0;
    }

#if SERIAL_MONITOR
    Serial.print("Microseconds for one run through Dhrystone: ");
    Serial.println(Microseconds);
    Serial.print("Dhrystones per Second: ");
    Serial.println(Dhrystones_Per_Second);
    Serial.print("VAX MIPS rating = ");
    Serial.println(Vax_Mips);
#endif

    ++dhry_ctr;
}


#endif    // DHRYLOAD_H
