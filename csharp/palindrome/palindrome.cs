using System;

public static class Palindrome
{
    public static bool IsPalindrome(string s)
    {
        if (s == null)
        {
            return false;
        }

        int left = 0;
        int right = s.Length - 1;

        while (left < right)
        {
            while (left < right && !char.IsLetterOrDigit(s[left]))
            {
                left++;
            }

            while (left < right && !char.IsLetterOrDigit(s[right]))
            {
                right--;
            }

            char l = char.ToLowerInvariant(s[left]);
            char r = char.ToLowerInvariant(s[right]);

            if (l != r)
            {
                return false;
            }

            left++;
            right--;
        }

        return true;
    }
}
