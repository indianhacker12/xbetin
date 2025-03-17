document.addEventListener("DOMContentLoaded", function () {
    let timerValue = 30;
    let timerInterval;
    const timerElement = document.getElementById("timer");
    const placeBetButton = document.getElementById("placeBetButton");
    let selectedBet = null;

    function startTimer() {
        clearInterval(timerInterval); // Clear any existing interval to prevent duplicate intervals
        timerValue = 30;
        timerElement.textContent = timerValue;

        timerInterval = setInterval(() => {
            if (timerValue > 0) {
                timerValue--;
                timerElement.textContent = timerValue;
            }
            if (timerValue === 7) {
                disableBetting();
            }
            if (timerValue === 0) {
                clearInterval(timerInterval);
                resetBetting();
            }
        }, 1000);
    }

    function disableBetting() {
        document.querySelectorAll('.option').forEach(btn => btn.style.pointerEvents = 'none');
        placeBetButton.disabled = true;
        placeBetButton.style.background = "gray";
    }

    function resetBetting() {
        document.querySelectorAll('.option').forEach(btn => btn.style.pointerEvents = 'auto');
        placeBetButton.disabled = false;
        placeBetButton.style.background = "aqua";
        timerValue = 30;
        fetchWalletBalance(); // Update wallet balance when betting resets
        startTimer();
    }

    function placeBet(type, value, multiplier) {
        const betAmount = document.getElementById("betAmount").value;
        if (!betAmount || betAmount < 1) {
            alert("Please enter a valid bet amount!");
            return;
        }
        selectedBet = { type, value, betAmount, multiplier };
        alert(`Bet selected: ${type} - ${value} | Amount: ₹${betAmount} | Multiplier: ${multiplier}`);
    }

    function updateHistory(type, value, amount, result) {
        let historyElement;
        if (type === "Color") {
            historyElement = document.getElementById("color-history");
        } else if (type === "Number") {
            historyElement = document.getElementById("number-history");
        } else if (type === "BigSmall") {
            historyElement = document.getElementById("bigsmall-history");
        }

        if (historyElement) {
            const newEntry = document.createElement("li");
            const resultClass = result === "win" ? "win" : "lose";
            newEntry.textContent = `${value} - ₹${amount} (${result})`;
            newEntry.classList.add(resultClass);
            historyElement.prepend(newEntry);
        }
    }

    function confirmBet() {
        if (!selectedBet) {
            alert("No bet selected!");
            return;
        }

        fetch('/place_bet', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(selectedBet)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById("walletBalance").textContent = data.new_balance.toFixed(2);
                updateHistory(selectedBet.type, selectedBet.value, selectedBet.betAmount, data.result);
                
                // Show result to user
                const resultMessage = data.result === "win" ? 
                    `You won! +₹${(selectedBet.betAmount * selectedBet.multiplier).toFixed(2)}` : 
                    `You lost! -₹${selectedBet.betAmount}`;
                alert(resultMessage);
                
                selectedBet = null; // Reset bet selection after confirmation
            } else {
                alert("Bet failed: " + data.error);
            }
        });
    }

    function fetchWalletBalance() {
        fetch('/get_wallet_balance')
            .then(response => response.json())
            .then(data => {
                if (data.wallet_balance !== undefined) {
                    document.getElementById("walletBalance").textContent = data.wallet_balance.toFixed(2);
                }
            })
            .catch(error => console.error("Error fetching balance:", error));
    }

    function updateHistory(type, value, amount) {
        let historyElement;
        if (type === "Color") {
            historyElement = document.getElementById("color-history");
        } else if (type === "Number") {
            historyElement = document.getElementById("number-history");
        } else if (type === "BigSmall") {
            historyElement = document.getElementById("bigsmall-history");
        }

        if (historyElement) {
            const newEntry = document.createElement("li");
            newEntry.textContent = `${value} - ₹${amount}`;
            historyElement.prepend(newEntry);
        }
    }

    function fetchBetHistory() {
        fetch('/get_bet_history')
            .then(response => response.json())
            .then(data => {
                if (data.bet_history) {
                    const colorHistory = document.getElementById("color-history");
                    const numberHistory = document.getElementById("number-history");
                    const bigSmallHistory = document.getElementById("bigsmall-history");

                    // Clear previous history
                    colorHistory.innerHTML = "";
                    numberHistory.innerHTML = "";
                    bigSmallHistory.innerHTML = "";

                    // Append new bet history
                    data.bet_history.forEach(bet => {
                        const newEntry = document.createElement("li");
                        newEntry.textContent = `${bet.value} - ₹${bet.amount}`;

                        if (bet.type === "Color") {
                            colorHistory.appendChild(newEntry);
                        } else if (bet.type === "Number") {
                            numberHistory.appendChild(newEntry);
                        } else if (bet.type === "BigSmall") {
                            bigSmallHistory.appendChild(newEntry);
                        }
                    });
                }
            })
            .catch(error => console.error("Error fetching bet history:", error));
    }

    document.querySelectorAll('.option').forEach(option => {
        option.addEventListener("click", function () {
            placeBet(this.dataset.type, this.dataset.value, this.dataset.multiplier);
        });
    });

    placeBetButton.addEventListener("click", confirmBet);

    fetchWalletBalance(); // Fetch wallet balance on page load
    fetchBetHistory(); // Fetch bet history on page load
    startTimer(); // Start the game timer
}); 