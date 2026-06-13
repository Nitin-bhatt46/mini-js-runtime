function reverseArray(arr) {
    let reversed = [];
    let len = arr.length;
    for (let i = len - 1; i >= 0; i = i - 1) {
        reversed.push(arr[i]);
    }
    return reversed;
}

let arr1 = [1, 2, 3, 4, 5];
console.log("Original: [" + arr1.join(", ") + "]");
console.log("Reversed: [" + reverseArray(arr1).join(", ") + "]");

let arr2 = ["apple", "banana", "cherry"];
console.log("Original: [" + arr2.join(", ") + "]");
console.log("Reversed: [" + reverseArray(arr2).join(", ") + "]");
