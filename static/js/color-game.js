let balance = 500.00;
let countdown = 60;
let timerInterval;
let bets = [];
let gameId = 1000; // Initialize a game ID counter

// Start countdown timer
function startTimer() {
    countdown = 60;
    document.getElementById("timer").innerText = countdown;
    enableBetting();

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
    if (countdown <= 5) {
        alert("Betting is disabled in the last 5 seconds!");
        return;
    }

    const betAmount = parseFloat(document.getElementById("betAmount").value);
    if (isNaN(betAmount) || betAmount <= 0) {
        alert("Please enter a valid bet amount!");
        return;
    }
    if (betAmount > balance) {
        alert("Insufficient balance!");
        return;
    }

    const bet = { game, option, multiplier, amount: betAmount };
    bets.push(bet);
    alert(`You selected ${game} - ${option} with multiplier ${multiplier} and bet amount ${betAmount.toFixed(2)}`);
}

// Confirm placing bets
function confirmBet() {
    if (bets.length === 0) {
        alert("Please place at least one bet.");
        return;
    }

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

// Evaluate the results of all placed bets
function evaluateBets() {
    if (bets.length === 0) {
        alert("No bets placed.");
        return;
    }

    const colorOutcomes = ["Red", "Green", "Violet"];
    const numberOutcomes = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"];
    const bigSmallOutcomes = ["Big", "Small"];
    let anyWin = false;

    bets.forEach(bet => {
        let winningOutcome;
        switch (bet.game) {
            case "Color":
                winningOutcome = colorOutcomes[Math.floor(Math.random() * colorOutcomes.length)];
                updateHistory("color-history", gameId, bet.option, winningOutcome);
                break;
            case "Number":
                winningOutcome = numberOutcomes[Math.floor(Math.random() * numberOutcomes.length)];
                updateHistory("number-history", gameId, bet.option, winningOutcome);
                break;
            case "BigSmall":
                winningOutcome = bigSmallOutcomes[Math.floor(Math.random() * bigSmallOutcomes.length)];
                updateHistory("bigsmall-history", gameId, bet.option, winningOutcome);
                break;
        }

        if (bet.option === winningOutcome) {
            const winnings = bet.amount * bet.multiplier;
            balance += winnings;
            showWinMessage(winnings, bet.game);
            anyWin = true;
        }
    });

    if (!anyWin) {
        showLoseMessage();
    }

    updateBalance();
}

// Show winning message
function showWinMessage(winnings, game) {
    const winDialog = document.getElementById("win_dialog");
    winDialog.style.display = "flex";
    winDialog.querySelector(".Congratulations_results").innerText = `You won ${winnings.toFixed(2)} on ${game}!`;
    winDialog.querySelector("h2").innerText = "Congratulations!";
}

// Show losing message
function showLoseMessage() {
    const loseDialog = document.getElementById("lost_dialog");
    loseDialog.style.display = "flex";
    loseDialog.querySelector(".Congratulations_results").innerText = "Better luck next time!";
    loseDialog.querySelector("h2").innerText = "You Lost";
}

// Update balance display
function updateBalance() {
    document.getElementById("balance").innerText = balance.toFixed(2);
}

// Update result history with game ID
function updateHistory(historyId, gameId, userBet, winningOutcome) {
    const historyList = document.getElementById(historyId);
    const resultItem = document.createElement("li");
    resultItem.textContent = `Game ID: ${gameId} | Bet: ${userBet} | Result: ${winningOutcome}`;
    historyList.appendChild(resultItem);
}

// Reset game for next round
function resetGame() {
    bets = [];
    gameId++; // Increment game ID for the next round

    // Hide dialogs
    document.getElementById("win_dialog").style.display = "none";
    document.getElementById("lost_dialog").style.display = "none";
    
    // Restart the timer
    startTimer();
}

// Enable and disable betting functions
function enableBetting() {
    document.getElementById("betButton").disabled = false;
}

function disableBetting() {
    document.getElementById("betButton").disabled = true;
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
