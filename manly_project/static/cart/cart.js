<script>
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.querySelectorAll(".add-to-cart-btn").forEach(btn => {
    btn.addEventListener("click", function () {
        if (btn.disabled) return;

        const productId = btn.dataset.productId;
        const variantId = document.getElementById("sizeSelect").value;

        if (!variantId) {
            alert("Please select a size");
            return;
        }

        btn.classList.add("loading");
        btn.querySelector(".btn-text").innerText = "Adding...";

        fetch("/cart/add/", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
                product_id: productId,
                variant_id: variantId,
                quantity: 1,
            }),
        })
        .then(res => res.json())
        .then(data => {
            btn.classList.remove("loading");

            if (data.success) {
                btn.classList.add("added");
                btn.querySelector(".btn-text").innerText = "Added";

               
                const cartCount = document.querySelector(".cart-count");
                if (cartCount) {
                    cartCount.innerText = data.cart_count;
                }
            } else {
                btn.querySelector(".btn-text").innerText = "Add to Cart";
                alert(data.message);
            }
        })
        .catch(() => {
            btn.classList.remove("loading");
            btn.querySelector(".btn-text").innerText = "Add to Cart";
            alert("Something went wrong");
        });
    });
});
</script>
