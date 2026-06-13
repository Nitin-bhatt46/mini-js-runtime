function isArmstrong(num) {
    let numStr = "" + num;
    let len = numStr.length;
    let sum = 0;
    for (let i = 0; i < len; i = i + 1) {
        let digit = +numStr[i];
        sum = sum + (digit ** len);
    }
    if (sum === num) {
        console.log(num + " is an Armstrong number");
    } else {
        console.log(num + " is not an Armstrong number");
    }
}

isArmstrong(153);
isArmstrong(370);
isArmstrong(123);
isArmstrong(9);
isArmstrong(1634);
