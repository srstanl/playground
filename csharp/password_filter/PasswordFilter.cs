using System;

// Password Filter (Multi-Rule Validator)
//
// Problem:
// Implement a password validator that returns true only if all rules are satisfied:
// 1) Length is between 8 and 20 characters (inclusive).
// 2) Contains at least 1 lowercase letter.
// 3) Contains at least 1 uppercase letter.
// 4) Contains at least 1 digit.
// 5) Contains at least 1 special character from: ! @ # $ % ^ & *
// 6) Must NOT be a palindrome when considering only alphanumeric characters,
//    case-insensitive (e.g., "A1b1a" is a palindrome).
// 7) No character may repeat more than 4 times in a row (e.g., "aaaaa" invalid).
// 8) Must NOT contain any banned substrings (case-insensitive):
//    ["password", "admin", "qwerty", "letmein", "welcome"]
//
// Notes:
// - You may assume ASCII input.
// - Treat null as invalid.
public static class PasswordFilter
{
    public static bool IsValid(string password)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
