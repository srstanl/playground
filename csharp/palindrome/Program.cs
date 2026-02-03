using System;
public static class Program
{
    public static void Main()
    {
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
