// Test scaffold for isPalindrome
// Use your preferred test runner (Jest/Mocha) to wire these cases.

const { isPalindrome } = require("./palindrome");

const cases = [
  { input: "A man, a plan, a canal: Panama", expected: true },
  { input: "race a car", expected: false },
  { input: " ", expected: true },
  { input: "0P", expected: false },
];

for (const testCase of cases) {
  const actual = isPalindrome(testCase.input);
  console.log(
    `Input: "${testCase.input}" -> expected ${testCase.expected}, got ${actual}`
  );
}
