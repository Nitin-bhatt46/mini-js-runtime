function isPalindrome(str) {
    let len = str.length;
    let palindrome = true;
    for (let i = 0; i < len / 2; i = i + 1) {
        if (str[i] != str[len - 1 - i]) {
            palindrome = false;
        }
    }
    if (palindrome) {
        console.log(str + " is a palindrome");
    } else {
        console.log(str + " is not a palindrome");
    }
}

isPalindrome("racecar");
isPalindrome("hello");
isPalindrome("madam");
isPalindrome("step on no pets");
