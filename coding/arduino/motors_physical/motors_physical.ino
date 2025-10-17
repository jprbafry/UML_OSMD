#define USE_ENCODERS 0  // <-- set 0 to compile without encoder support (open-loop)
 
// === Pin Definitions ===
// Make sure pins match your setup
#define DET_AZ_STEP 34
#define DET_AZ_DIR 35
#define DET_RAD_STEP 32
#define DET_RAD_DIR 33
#define LIGHT_AZ_STEP 36
#define LIGHT_AZ_DIR 37
#define LIGHT_RAD_STEP 30
#define LIGHT_RAD_DIR 31

// === Encoder pins (change to match your wiring) ===
// A channels must be interrupt capable
#define DET_AZ_ENC_A 2
#define DET_RAD_ENC_A 3
#define LIGHT_AZ_ENC_A 18
#define LIGHT_RAD_ENC_A 19
// B channels normal digital input
#define DET_AZ_ENC_B 13
#define DET_RAD_ENC_B 12
#define LIGHT_AZ_ENC_B 11
#define LIGHT_RAD_ENC_B 10

const int ENC_A_PINS[4] = { DET_AZ_ENC_A,  DET_RAD_ENC_A, LIGHT_AZ_ENC_A, LIGHT_RAD_ENC_A };
const int ENC_B_PINS[4] = { DET_AZ_ENC_B, DET_RAD_ENC_B, LIGHT_AZ_ENC_B, LIGHT_RAD_ENC_B };

// === Constants ===
// TODO: Change if necessary (how many steps the motor does per degree depends on the setup)
const float DET_AZ_STEPS_PER_DEG = 12.0;
const float DET_RAD_STEPS_PER_DEG = 10.0;
const float LIGHT_AZ_STEPS_PER_DEG = 12.0;
const float LIGHT_RAD_STEPS_PER_DEG = 10.0;

const unsigned int NUM_MOTORS = 4; // How many motors do we have
const unsigned int STEP_DELAY_US = 500;  // Motor speed control

// Encoder constants TODO: Change if neccesary (set to your driver microstepping / encoder spec)
const int PULSES_PER_REV        = 1600;  // Microstepping. Parameter selected in the motor driver. Change it if needed.
const int ENCODER_CPR           = 512;   // Counts per rev. Precision of the encoder. Given in the datasheet. 
const int ENCODER_COUNTS_PER_REV  = ENCODER_CPR * 2;  // We count only A edges -> 2 counts per quadrature cycle
const float COUNTS_PER_PULSE = (float)ENCODER_COUNTS_PER_REV / (float)PULSES_PER_REV; // How many times we count per pulse.

// === State ===
volatile long encoder_counts[NUM_MOTORS] = {0,0,0,0};

// === Enum for Axis Selection ===
enum MotorAxis {
  DETECTOR_AZ,
  DETECTOR_RAD,
  LIGHT_AZ,
  LIGHT_RAD
};

// === Motor struct ===
struct Motor {
  const char *name;
  int step_pin;
  int dir_pin;
  int enc_a;
  int enc_b;
  float steps_per_deg;
  long current_steps;     // stored "actual" steps (updated from encoder)
};

Motor motors[NUM_MOTORS];

// === Function Prototypes ===
void move_to_absolute(MotorAxis axis, float target_angle);
void reset_position();
Motor* get_motor(MotorAxis axis);

#if USE_ENCODERS
// ================= ISRs =================
// The ISRs are called when there is a change on signal A this is as there is not enough pins
// available for interrupts on both A and B.
// Keep ISRs tiny and fast: read A and B and increment/decrement encoder_counts[idx].
void isr_enc0() {
  bool a = digitalRead(ENC_A_PINS[0]);
  bool b = digitalRead(ENC_B_PINS[0]);
  if (a == b) encoder_counts[0] += 1;
  else        encoder_counts[0] -= 1;
}
void isr_enc1() {
  bool a = digitalRead(ENC_A_PINS[1]);
  bool b = digitalRead(ENC_B_PINS[1]);
  if (a == b) encoder_counts[1] += 1;
  else        encoder_counts[1] -= 1;
}
void isr_enc2() {
  bool a = digitalRead(ENC_A_PINS[2]);
  bool b = digitalRead(ENC_B_PINS[2]);
  if (a == b) encoder_counts[2] += 1;
  else        encoder_counts[2] -= 1;
}
void isr_enc3() {
  bool a = digitalRead(ENC_A_PINS[3]);
  bool b = digitalRead(ENC_B_PINS[3]);
  if (a == b) encoder_counts[3] += 1;
  else        encoder_counts[3] -= 1;
}
#endif // USE_ENCODERS

// ================ Utilities =================
long atomic_read_encoder(int idx) {
#if USE_ENCODERS

  noInterrupts();
  long v = encoder_counts[idx];
  interrupts();
  return v;
#else
  (void)idx;
  return 0L;
#endif
}
void atomic_write_encoder(int idx, long v) {
#if USE_ENCODERS  
  noInterrupts();
  encoder_counts[idx] = v;
  interrupts();
#else
  (void)idx;
  (void)v;
#endif
}

Motor* get_motor(MotorAxis axis) {
  return &motors[(int)axis];
}

void setup() {
  Serial.begin(9600);

  // initialize motor table (match pins and initial 8 degrees)
  motors[DETECTOR_AZ]  = {"DET_AZ",  DET_AZ_STEP,  DET_AZ_DIR,  DET_AZ_ENC_A,  DET_AZ_ENC_B,  DET_AZ_STEPS_PER_DEG,  long(8 * DET_AZ_STEPS_PER_DEG)};
  motors[DETECTOR_RAD] = {"DET_RAD", DET_RAD_STEP, DET_RAD_DIR, DET_RAD_ENC_A, DET_RAD_ENC_B, DET_RAD_STEPS_PER_DEG, long(8 * DET_RAD_STEPS_PER_DEG)};
  motors[LIGHT_AZ]     = {"LIGHT_AZ",LIGHT_AZ_STEP, LIGHT_AZ_DIR, LIGHT_AZ_ENC_A, LIGHT_AZ_ENC_B, LIGHT_AZ_STEPS_PER_DEG, long(8 * LIGHT_AZ_STEPS_PER_DEG)};
  motors[LIGHT_RAD]    = {"LIGHT_RAD",LIGHT_RAD_STEP, LIGHT_RAD_DIR, LIGHT_RAD_ENC_A, LIGHT_RAD_ENC_B, LIGHT_RAD_STEPS_PER_DEG, long(8 * LIGHT_RAD_STEPS_PER_DEG)};

   // Setup pins and encoders
  for (int i = 0; i < NUM_MOTORS; ++i) {
    pinMode(motors[i].step_pin, OUTPUT);
    pinMode(motors[i].dir_pin, OUTPUT);
    pinMode(motors[i].enc_a, INPUT_PULLUP);
    pinMode(motors[i].enc_b, INPUT_PULLUP);
    atomic_write_encoder(i, 0);
  }

#if USE_ENCODERS
  // Attach interrupts to the A pins. Interrupt enters when there is a CHANGE in the signal on pin A.
  attachInterrupt(digitalPinToInterrupt(ENC_A_PINS[0]), isr_enc0, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_A_PINS[1]), isr_enc1, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_A_PINS[2]), isr_enc2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_A_PINS[3]), isr_enc3, CHANGE);
#endif 

  Serial.println("Motor controller ready.");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.length() == 0) {
      return;
    }

    if (command == "RESET_POS") {
      reset_position();
      return;
    }

    int colonIndex = command.indexOf(':');
    if (colonIndex == -1) {
      Serial.println("Invalid format.");
      return;
    }

    String target = command.substring(0, colonIndex);
    float angle = command.substring(colonIndex + 1).toFloat();

    if (target == "DET_AZ_ABS") {
      move_to_absolute(DETECTOR_AZ, angle);
    } else if (target == "DET_RAD_ABS") {
      move_to_absolute(DETECTOR_RAD, angle);
    } else if (target == "LIGHT_AZ_ABS") {
      move_to_absolute(LIGHT_AZ, angle);
    } else if (target == "LIGHT_RAD_ABS") {
      move_to_absolute(LIGHT_RAD, angle);
    } else {
      Serial.println("Unknown command.");
    }
  }
}

void move_to_absolute(MotorAxis axis, float target_angle) {
  Motor* m = get_motor(axis);

  long target_steps = lround(target_angle * m->steps_per_deg);
  long step_diff = target_steps - m->current_steps;
  bool direction = (step_diff >= 0);
  long move_steps = abs(step_diff);

  // Read encoder before moving
  long enc_before = atomic_read_encoder((int)axis);

  digitalWrite(m->dir_pin, direction ? HIGH : LOW);
  for (long i = 0; i < move_steps; i++) {
    digitalWrite(m->step_pin, HIGH);
    delayMicroseconds(STEP_DELAY_US);
    digitalWrite(m->step_pin, LOW);
    delayMicroseconds(STEP_DELAY_US);
  }

  long starting_pos = m->current_steps;

#if USE_ENCODERS
  // Read encoder AFTER moving
  long enc_after = atomic_read_encoder((int)axis);
  long delta_counts = enc_after - enc_before;

  // Convert encoder counts -> motor steps
  float measured_steps_float = (float)delta_counts / COUNTS_PER_PULSE;
  long measured_steps = lround(-measured_steps_float);

  m->current_steps += measured_steps;
#else
  m->current_steps = target_steps;
#endif

  Serial.print("Moved ");
  Serial.print(m->name);
  Serial.print(" from ");
  Serial.print(lround((float)starting_pos / m->steps_per_deg));
  Serial.print(" to ");
  Serial.print(target_angle, 2);
  Serial.print(" degrees. (");
  Serial.print(move_steps);
  Serial.println(" steps)");
  Serial.println("OK");
}

void reset_position() {
  for (int i = 0; i < NUM_MOTORS; ++i) {
    motors[i].current_steps = long(8 * motors[i].steps_per_deg);
#if USE_ENCODERS
    long encoder_baseline = (long)lround((float)motors[i].current_steps * -COUNTS_PER_PULSE);
    atomic_write_encoder(i, encoder_baseline);
#else
    encoder_counts[i] = 0;
#endif
  }

  Serial.println("Position reset to 8 degrees on all axes.");
  Serial.println("OK");
}