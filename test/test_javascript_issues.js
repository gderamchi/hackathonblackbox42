/**
 * Test JavaScript file with intentional bugs and security issues
 * for PR review bot testing.
 */

// SECURITY ISSUE: Hardcoded API credentials
const API_KEY = "sk-abcdef123456789";
const SECRET_TOKEN = "secret_token_12345";

// BUG: Using var instead of let/const
var globalVariable = "should use let or const";

// BUG: Using == instead of ===
function checkValue(value) {
    if (value == null) {
        return false;
    }
    return true;
}

// BUG: Using != instead of !==
function compareValues(a, b) {
    if (a != b) {
        return false;
    }
    return true;
}

// SECURITY ISSUE: XSS vulnerability with innerHTML
function displayUserContent(userInput) {
    document.getElementById('content').innerHTML = userInput;
}

// SECURITY ISSUE: Using eval
function executeCode(code) {
    eval(code);
}

// BUG: Console.log in production
console.log("Debug: Application initialized");
console.log("API Key:", API_KEY);

// BUG: Debugger statement
function debugFunction() {
    debugger;
    return "debugging";
}

// SECURITY ISSUE: SQL injection in template string
function getUserData(userId) {
    const query = `SELECT * FROM users WHERE id = ${userId}`;
    return executeQuery(query);
}

// BUG: Potential null/undefined access
function processUser(user) {
    console.log(user.name);
    console.log(user.email);
    return user.id;
}

// BUG: Array.sort() modifies in place
function sortArray(arr) {
    return arr.sort();
}

// BUG: Async function without await
async function fetchData() {
    return getData();
}

// BUG: Potential infinite loop
function processItems() {
    while (true) {
        processItem();
    }
}

// SECURITY ISSUE: Command injection
function runCommand(cmd) {
    const { exec } = require('child_process');
    exec(cmd);
}

// BUG: String concatenation instead of template literals
function buildMessage(name, age) {
    return "Hello " + name + ", you are " + age + " years old";
}

// SECURITY ISSUE: Insecure random number generation
function generateToken() {
    return Math.random().toString(36);
}

// BUG: Comparison with length without null check
function checkArray(arr) {
    if (arr.length > 0) {
        return true;
    }
    return false;
}

// TODO: Fix security issues
// FIXME: Remove hardcoded credentials
// HACK: Temporary solution

module.exports = {
    checkValue,
    displayUserContent,
    executeCode,
    getUserData
};
