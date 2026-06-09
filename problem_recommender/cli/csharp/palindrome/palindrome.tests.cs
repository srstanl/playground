using System;

// Test scaffold for Palindrome.IsPalindrome
// Use your preferred test framework (xUnit/NUnit/MSTest) to wire these cases.
public static class PalindromeTests
{
    public static void Run()
    {
        // TODO: replace with real assertions in your test runner.
        var cases = new (string input, bool expected)[]
        {
            ("A man, a plan, a canal: Panama", true),
            ("race a car", false),
            (" ", true),
            ("0P", false)
        };

        foreach (var testCase in cases)
        {
            bool actual = Palindrome.IsPalindrome(testCase.input);
            Console.WriteLine(
                $"Input: \"{testCase.input}\" -> expected {testCase.expected}, got {actual}");
        }
    }
}
