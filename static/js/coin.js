function flipCoin() {
    const resultElement = document.getElementById("result");
    const coin = document.querySelector(".coin");
    const isHeads = Math.random() < 0.5;

    coin.style.transition = "transform 1s";
    coin.style.transform = "rotateY(1800deg)";

    setTimeout(() => {
        coin.style.transition = "";
        coin.style.transform = isHeads ? "rotateY(0deg)" : "rotateY(180deg)";
        resultElement.textContent = isHeads ? "It's Heads!" : "It's Tails!";
    }, 1000);
}
