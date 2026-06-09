import React, { useState, useContext } from "react";
import { register, login } from "../services/api";
import { useNavigate } from "react-router-dom";
import "../styles/login.css";
import { LoadingContext } from "../context/LoadingContext";

export default function Login() {
  const [phone, setPhone] = useState("");
  const [name, setName] = useState("");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [isRegister, setIsRegister] = useState(false);

  const navigate = useNavigate();
  const { setLoading } = useContext(LoadingContext);

  const handleSubmit = async () => {
    if (!phone.trim()) {
      alert("Enter phone number");
      return;
    }

    if (!/^\d{10}$/.test(phone)) {
      alert("Phone number must be exactly 10 digits");
      return;
    }

    if (isRegister) {
      if (!name.trim()) {
        alert("Enter name");
        return;
      }

      if (!password) {
        alert("Enter password");
        return;
      }

      if (password.length < 8) {
        alert("Password must be at least 8 characters");
        return;
      }

      if (!confirmPassword) {
        alert("Confirm your password");
        return;
      }

      if (password !== confirmPassword) {
        alert("Passwords do not match");
        return;
      }
    } else {
      if (!password) {
        alert("Enter password");
        return;
      }

      if (password.length < 8) {
        alert("Password must be at least 8 characters");
        return;
      }
    }

    try {
      setLoading(true);

      if (isRegister) {
        const registerResponse = await register(
          phone,
          name,
          password,
          confirmPassword
        );

        if (registerResponse.error) {
          alert(registerResponse.error);
          return;
        }
      }

      const res = await login(
        phone,
        password
      );

      if (res.user) {

        localStorage.setItem(
          "user",
          JSON.stringify(res.user)
        );

        localStorage.setItem(
          "token",
          res.token
        );

        navigate("/dashboard");

      } else {

        alert(
          res.error || "Login failed"
        );
      }

    } catch (err) {

    console.error(err);

    alert(
      err?.response?.data?.detail ||
      err?.response?.data?.error ||
      err?.message ||
      "Something went wrong"
    );
  } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="card login-box">

        <h2 className="login-title">
          Insurance Claim System
        </h2>

        {isRegister && (
          <input
            placeholder="Name"
            value={name}
            onChange={(e) =>
              setName(e.target.value)
            }
          />
        )}

        <input
          placeholder="Phone Number"
          value={phone}
          onChange={(e) =>
            setPhone(e.target.value)
          }
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
        />

        {isRegister && (
          <input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) =>
              setConfirmPassword(e.target.value)
            }
          />
        )}

        <button onClick={handleSubmit}>
          {isRegister
            ? "Register & Login"
            : "Login"}
        </button>

        <p
          className="switch-text"
          onClick={() =>
            setIsRegister(!isRegister)
          }
        >
          {isRegister
            ? "Login instead"
            : "Register instead"}
        </p>

      </div>
    </div>
  );
}