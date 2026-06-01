

import React, { useState, useContext } from "react";
import { register, login } from "../services/api";
import { useNavigate } from "react-router-dom";
import "../styles/login.css";
import { LoadingContext } from "../context/LoadingContext";

export default function Login() {

  const [phone, setPhone] = useState("");
  const [name, setName] = useState("");
  const [isRegister, setIsRegister] = useState(false);

  const navigate = useNavigate();
  const { setLoading } = useContext(LoadingContext);

  const handleSubmit = async () => {

    if (!phone) {
      alert("Enter phone number");
      return;
    }

    try {
      setLoading(true); // ✅ START

      if (isRegister) {
        await register(phone, name);
      }

      const res = await login(phone);

      if (res.user) {
        localStorage.setItem("user", JSON.stringify(res.user));
        localStorage.setItem("token", res.token);
        navigate("/dashboard");
      } else {
        alert(res.error || "Login failed");
      }

    } catch (err) {
      console.error(err);
      alert("Something went wrong");
    } finally {
      setLoading(false); // ✅ END
    }
  };

  return (
    <div className="page">
      <div className="card login-box">

        <h2 className="login-title">Interview claim system</h2>

        {isRegister && (
          <input
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        )}

        <input
          placeholder="Phone Number"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
        />

        <button onClick={handleSubmit}>
          {isRegister ? "Register & Login" : "Login"}
        </button>

        <p
          className="switch-text"
          onClick={() => setIsRegister(!isRegister)}
        >
          {isRegister ? "Login instead" : "Register instead"}
        </p>

      </div>
    </div>
  );
}