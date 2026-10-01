import bcrypt from "bcryptjs";

async function testHashing() {
  const password = "MyPassword123";
  const hashedPassword = await bcrypt.hash(password, 12);

// this 12 stands for the salt rounds, which determines the computational cost of hashing. A higher number means more security but also more time to compute.
  console.log("Original password:", password);
  console.log("Hashed password:", hashedPassword);

  // Step 2: Compare the original password
  const isCorrect = await bcrypt.compare(
    password,
    hashedPassword
  );

  console.log("Correct password:", isCorrect);

  // Step 3: Compare a wrong password
  const isWrong = await bcrypt.compare(
    "WrongPassword",
    hashedPassword
  );

  console.log("Wrong password:", isWrong);
}

testHashing();