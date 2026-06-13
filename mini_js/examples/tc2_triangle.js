function classifyTriangle(a, b, c) {
    if (a + b <= c || a + c <= b || b + c <= a) {
        console.log("Invalid");
    } else if (a === b && b === c) {
        console.log("Equilateral");
    } else if (a === b || b === c || a === c) {
        console.log("Isosceles");
    } else {
        console.log("Scalene");
    }
}

classifyTriangle(3, 3, 3);
classifyTriangle(3, 4, 4);
classifyTriangle(3, 4, 5);
classifyTriangle(1, 2, 3);
