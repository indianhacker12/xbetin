
let gameId = Math.floor(Math.random() * 100000000).toString().padStart(8, '0');
let walletBalance = 1000;
let selectedColor = '';
let timerInterval;
const colors = ['Red', 'Green', 'Violet'];
const payouts = { 'Red': 1.97, 'Green': 1.97, 'Violet': 4.5 };

document.getElementById('game-id').textContent = gameId;
document.getElementById('wallet-balance').textContent = walletBalance;

function startTimer() {
    let timeRemaining = 30;
    document.getElementById('timer').textContent = formatTime(timeRemaining);

    timerInterval = setInterval(() => {
        timeRemaining--;
        document.getElementById('timer').textContent = formatTime(timeRemaining);

        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            runGame();
            startNewRound();
        }
    }, 1000);
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function runGame() {
    const winningColor = colors[Math.floor(Math.random() * colors.length)];
    let resultMessage = 'You lost!';
    let resultColor = 'red';

    if (selectedColor === winningColor) {
        walletBalance += parseFloat(document.getElementById('bet-amount').value) * payouts[winningColor];
        resultMessage = 'You won!';
        resultColor = 'green';
    } else {
        walletBalance -= parseFloat(document.getElementById('bet-amount').value);
    }

    document.getElementById('wallet-balance').textContent = walletBalance;
    document.getElementById('message').textContent = resultMessage;
    document.getElementById('message').style.color = resultColor;

    addToHistory(winningColor, resultMessage);
}

function addToHistory(winningColor, result) {
    const historyTable = document.getElementById('history');
    const row = document.createElement('tr');
    const period = document.createElement('td');
    const color = document.createElement('td');
    const resultCell = document.createElement('td');
    const timeCell = document.createElement('td');
    const colorBox = document.createElement('td');

    period.textContent = gameId;
    color.textContent = winningColor;
    resultCell.textContent = result;
    timeCell.textContent = new Date().toLocaleTimeString();

    colorBox.style.backgroundColor = winningColor.toLowerCase();
    colorBox.classList.add('color-box');

    row.appendChild(period);
    row.appendChild(color);
    row.appendChild(colorBox);
    row.appendChild(resultCell);
    row.appendChild(timeCell);
    historyTable.appendChild(row);
}

function resetGame() {
    gameId = Math.floor(Math.random() * 100000000).toString().padStart(8, '0');
    document.getElementById('game-id').textContent = gameId;
    selectedColor = '';
    document.getElementById('bet-amount').value = 10;
}

function selectColor(color) {
    selectedColor = color;
    document.querySelectorAll('.color').forEach(button => {
        button.style.border = 'none';
    });
    document.querySelector(`.color.${color.toLowerCase()}`).style.border = '2px solid #fff';
}

function placeBet() {
    const betAmount = parseFloat(document.getElementById('bet-amount').value);
    if (isNaN(betAmount) || betAmount <= 0 || betAmount > walletBalance) {
        alert('Please enter a valid bet amount.');
        return;
    }
    if (!selectedColor) {
        alert('Please select a color.');
        return;
    }

    document.getElementById('message').textContent = 'Bet placed! Waiting for the result...';
    document.getElementById('message').style.color = '#000';
}

function startNewRound() {
    resetGame();
    startTimer();
}

window.onload = () => {
    startTimer();
};
