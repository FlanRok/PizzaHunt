document.addEventListener("DOMContentLoaded", function () {
  // Обработка изменения количества
  document.querySelectorAll(".quantity-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const itemId = this.dataset.itemId;
      const input = document.querySelector(
        `.quantity-input[data-item-id="${itemId}"]`
      );
      let quantity = parseInt(input.value);

      if (this.classList.contains("plus")) {
        quantity += 1;
      } else if (this.classList.contains("minus")) {
        quantity = Math.max(1, quantity - 1);
      }

      input.value = quantity;
      updateCartItem(itemId, quantity);
    });
  });

  // Обработка прямого ввода количества
  document.querySelectorAll(".quantity-input").forEach((input) => {
    input.addEventListener("change", function () {
      const itemId = this.dataset.itemId;
      const quantity = parseInt(this.value);

      if (quantity < 1) {
        this.value = 1;
        return;
      }

      updateCartItem(itemId, quantity);
    });
  });

  // Удаление товара
  document.querySelectorAll(".remove-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const itemId = this.dataset.itemId;
      if (confirm("Удалить товар из корзины?")) {
        removeCartItem(itemId);
      }
    });
  });

  // Функция обновления количества товара
  function updateCartItem(itemId, quantity) {
    fetch("/cart/update/", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: `item_id=${itemId}&quantity=${quantity}`,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          document.querySelectorAll(".cart-count").forEach((el) => {
            el.textContent = data.cart_quantity;
          });

          const itemElement = document.querySelector(
            `.cart-item[data-item-id="${itemId}"]`
          );
          if (itemElement) {
            const totalPriceElement = itemElement.querySelector(".total-price");
            if (totalPriceElement && data.item_total) {
              totalPriceElement.textContent = `${data.item_total.toFixed(2)} ₽`;
            }
          }

          const cartTotalElements = document.querySelectorAll(".cart-total");
          cartTotalElements.forEach((el) => {
            if (el.classList.contains("summary-value")) {
              el.textContent = `${data.cart_total.toFixed(2)} ₽`;
            } else if (el.classList.contains("summary-total")) {
              const deliveryCost = data.cart_total > 1000 ? 0 : 200;
              el.textContent = `${(data.cart_total + deliveryCost).toFixed(
                2
              )} ₽`;
            }
          });
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  // Функция удаления товара
  function removeCartItem(itemId) {
    fetch(`/cart/remove/${itemId}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken"),
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          const itemElement = document.querySelector(
            `.cart-item[data-item-id="${itemId}"]`
          );
          if (itemElement) {
            itemElement.remove();
          }

          document.querySelectorAll(".cart-count").forEach((el) => {
            el.textContent = data.cart_quantity;
          });

          if (data.cart_quantity === 0) {
            location.reload();
          }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
