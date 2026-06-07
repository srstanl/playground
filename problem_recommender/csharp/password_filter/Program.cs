using System;

public static class Program
{
    public static void Main()
    {
        var cases = new (string input, bool expected)[]
        {
            ("A1b!cdef", true),          // meets all rules
            ("A1b!cdefA1b!cdef", true),  // length 16, still valid
            ("racecar!", false),         // palindrome (alnum, case-insensitive)
            ("aaaaaA1!", false),         // 5 consecutive 'a'
            ("Admin123!", false),        // contains banned substring "admin"
            ("Short1!", false),          // too short
            ("NOLOWER1!", false),        // missing lowercase
            ("noupper1!", false),        // missing uppercase
            ("NoDigit!!", false),        // missing digit
            ("NoSpecial1", false)        // missing special
        };

        foreach (var testCase in cases)
        {
            bool actual = PasswordFilter.IsValid(testCase.input);
            Console.WriteLine(
                $"Input: \"{testCase.input}\" -> expected {testCase.expected}, got {actual}");
        }
    }
}
