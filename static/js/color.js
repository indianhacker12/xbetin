
let balance = 500.00;
let countdown = 30;
let timerInterval;
let bets = []; // Array to store multiple bets

// Start countdown timer
function startTimer() {
    countdown = 30;
    document.getElementById("timer").innerText = countdown;
    timerInterval = setInterval(() => {
        countdown--;
        document.getElementById("timer").innerText = countdown;
        if (countdown === 5) disableBetting();
        if (countdown <= 0) {
            clearInterval(timerInterval);
            evaluateBets();
            resetGame();
        }
    }, 1000);
}

// Place a bet selection
function placeBet(game, option, multiplier) {
const betAmount = parseFloat(document.getElementById("betAmount").value);
if (isNaN(betAmount) || betAmount <= 0) {
alert("Please enter a valid bet amount!");
return;
}

// Send a request to the backend
fetch('/place_bet', {
method: 'POST',
headers: {
    'Content-Type': 'application/json',
},
body: JSON.stringify({
    user_id: 1,  // Pass actual user ID here
    game: game,
    option: option,
    multiplier: multiplier,
    bet_amount: betAmount
})
})
.then(response => response.json())
.then(data => {
if (data.error) {
    alert(data.error);
} else {
    document.getElementById("balance").innerText = data.balance.toFixed(2);
    alert(`You ${data.result}! Winnings: ${data.winnings.toFixed(2)}. Winning option: ${data.winning_option}`);
}
})
.catch(error => console.error('Error:', error));
}
function placeBet(game, option, multiplier) {
const betAmount = parseFloat(document.getElementById("betAmount").value);
if (isNaN(betAmount) || betAmount <= 0) {
alert("Please enter a valid bet amount!");
return;
}

// Send a request to the backend
fetch('/place_bet', {
method: 'POST',
headers: {
    'Content-Type': 'application/json',
},
body: JSON.stringify({
    user_id: 1,  // Pass actual user ID here
    game: game,
    option: option,
    multiplier: multiplier,
    bet_amount: betAmount
})
})
.then(response => response.json())
.then(data => {
if (data.error) {
    alert(data.error);
} else {
    document.getElementById("balance").innerText = data.balance.toFixed(2);
    alert(`You ${data.result}! Winnings: ${data.winnings.toFixed(2)}. Winning option: ${data.winning_option}`);
}
})
.catch(error => console.error('Error:', error));
}

function fetchBalance() {
fetch('/get_balance/1')  // Pass actual user ID here
.then(response => response.json())
.then(data => {
if (data.balance) {
    document.getElementById("balance").innerText = data.balance.toFixed(2);
}
})
.catch(error => console.error('Error:', error));
}

// Call fetchBalance on page load
document.addEventListener("DOMContentLoaded", function() {
fetchBalance();
});

// Confirm placing bets
function confirmBet() {
    if (bets.length === 0) {
        alert("Please place at least one bet.");
        return;
    }

    // Deduct the total amount of all placed bets from the balance
    let totalBetAmount = 0;
    bets.forEach(bet => totalBetAmount += bet.amount);
    if (totalBetAmount > balance) {
        alert("Insufficient balance to place all bets!");
        return;
    }

    balance -= totalBetAmount;
    updateBalance();
    alert(`You placed ${bets.length} bets for a total of ${totalBetAmount.toFixed(2)}`);
}

// Disable betting in the last 5 seconds
function disableBetting() {
    document.querySelectorAll(".option").forEach(option => {
        option.style.pointerEvents = "none";
        option.style.opacity = "0.5";
    });
}

// Enable betting
function enableBetting() {
    document.querySelectorAll(".option").forEach(option => {
        option.style.pointerEvents = "auto";
        option.style.opacity = "1";
    });
}

// Evaluate the results of all placed bets
function evaluateBets() {
    if (bets.length === 0) {
        alert("No bets placed.");
        return;
    }

    const colorOutcomes = ["Red", "Green", "Violet"];
    const numberOutcomes = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
    const bigSmallOutcomes = ["Big", "Small"];

    bets.forEach(bet => {
        let winningOutcome;
        switch (bet.game) {
            case "Color":
                winningOutcome = colorOutcomes[Math.floor(Math.random() * colorOutcomes.length)];
                updateHistory("color-history", bet.option, winningOutcome);
                break;
            case "Number":
                winningOutcome = numberOutcomes[Math.floor(Math.random() * numberOutcomes.length)];
                updateHistory("number-history", bet.option, winningOutcome);
                break;
            case "BigSmall":
                winningOutcome = bigSmallOutcomes[Math.floor(Math.random() * bigSmallOutcomes.length)];
                updateHistory("bigsmall-history", bet.option, winningOutcome);
                break;
        }

        if (bet.option === winningOutcome) {
            const winnings = bet.amount * bet.multiplier;
            balance += winnings;
            alert(`You won ${winnings.toFixed(2)} for your ${bet.game} bet!`);
        } else {
            alert(`You lost your ${bet.game} bet.`);
        }
    });
    updateBalance();
}

// Update balance display
function updateBalance() {
    document.getElementById("balance").innerText = balance.toFixed(2);
}

// Update result history
function updateHistory(historyId, userBet, winningOutcome) {
    const historyList = document.getElementById(historyId);
    const resultItem = document.createElement("li");
    resultItem.textContent = `Bet: ${userBet} | Result: ${winningOutcome}`;
    historyList.appendChild(resultItem);
}

// Reset game for next round
function resetGame() {
    bets = [];
    enableBetting();
    startTimer();
}

// Deposit function
function deposit() {
    let depositAmount = prompt("Enter deposit amount:");
    if (depositAmount && !isNaN(depositAmount)) {
        balance += parseFloat(depositAmount);
        updateBalance();
    }
}

// Initialize game
startTimer();
