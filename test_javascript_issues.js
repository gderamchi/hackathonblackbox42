/**
 * Test JavaScript file with intentional issues
 * For PR review bot testing
 */

// Security Issue 1: XSS vulnerability
function displayUserInput(input) {
    document.getElementById('output').innerHTML = input; // XSS risk!
}

// Security Issue 2: eval usage
function executeCode(code) {
    eval(code); // Major security risk!
}

// Bug 1: Loose equality
function checkValue(value) {
    if (value == null) { // Should use ===
        return false;
    }
    return true;
}

// Bug 2: var instead of let/const
function oldStyle() {
    var x = 10; // Should use let or const
    var y = 20;
    return x + y;
}

// Code Quality Issue: console.log in production
function processData(data) {
    console.log('Processing:', data); // Remove before production
    return data.toUpperCase();
}

// Bug 3: Potential null/undefined access
function getUserName(user) {
    return user.name.toUpperCase(); // What if user or user.name is null?
}

// Security Issue 3: Hardcoded credentials
const API_KEY = 'abc123def456ghi789';
const SECRET = 'my-secret-key-12345';

// Bug 4: Infinite loop
function processItems(items) {
    while (true) {
        items.forEach(item => console.log(item));
        // Missing break!
    }
}

// Code Quality Issue: String concatenation
function buildMessage(name, age) {
    return 'Hello ' + name + ', you are ' + age + ' years old'; // Use template literals
}

// Bug 5: Async without await
async function fetchData() {
    // Async function but no await used
    return fetch('https://api.example.com/data');
}

// Security Issue 4: SQL injection (if using database)
function getUser(userId) {
    const query = "SELECT * FROM users WHERE id = " + userId; // SQL injection
    return db.query(query);
}

// Bug 6: Array mutation
function sortArray(arr) {
    return arr.sort(); // Mutates original array
}

// Code Quality Issue: Debugger statement
function debugFunction() {
    debugger; // Remove before commit
    return 'test';
}

// Bug 7: Type coercion issues
function add(a, b) {
    return a + b; // What if a is string and b is number?
}

// Security Issue 5: Insecure random
function generateToken() {
    return Math.random().toString(36); // Not cryptographically secure
}

// Main execution
const user = getUserData();
displayUserInput(user.input); // XSS
console.log(API_KEY); // Logging secrets
