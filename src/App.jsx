// src/App.jsx
import "./styles/index.scss";

import "@fortawesome/fontawesome-svg-core/styles.css";
import "react-calendar/dist/Calendar.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import AOS from "aos";
import "aos/dist/aos.css";
import { useEffect, useState } from "react";
import Context from "@/context/Context";
import HomePage1 from "./pages";
import api from "./api/axios";

// Imports do Dashboard
import DashboardPage from "./pages/dashboard/dashboard";
import DshbListingPage from "./pages/dashboard/dshb-listing";
import DshbSettingsPage from "./pages/dashboard/dshb-settings";
import DshbAdministrationPage from "./pages/dashboard/dshb-administration";
import DshbAssignmentPage from "./pages/dashboard/dshb-planejamento";
import DshbCalenderPage from "./pages/dashboard/dshb-calendar";
import DshbDashboardPage from "./pages/dashboard/dshb-notas";
import DshbDictionaryPage from "./pages/dashboard/dshb-emprestimo";
import DshbReservasPage from "./pages/dashboard/dshb-reservas";

// Imports das Páginas de Autenticação e Outras
import LoginPage from "./pages/others/login";
import ForgotPasswordPage from './pages/others/ForgotPasswordPage';
import ResetPasswordPage from './pages/others/ResetPasswordPage';   
import ScrollTopBehaviour from "./components/common/ScrollTopBehaviour";
import NotFoundPage from "./pages/not-found";

function App() {
  const [alunos, setAlunos] = useState([]);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    AOS.init({
      duration: 700,
      offset: 120,
      easing: "ease-out",
      once: true,
    });
  }, []);

  useEffect(() => {
    // Esta chamada de API para buscar 'alunos' provavelmente falhará
    // pois o endpoint está protegido e a requisição ainda não envia o token.
    api
      .get("alunos/")
      .then((response) => {
        if (Array.isArray(response.data)) {
          setAlunos(response.data);
        } else {
          setAlunos([]);
          setErro("Resposta da API não é uma lista.");
        }
      })
      .catch((error) => setErro(error.message));
  }, []);

  return (
    <>
      <Context>
        <BrowserRouter>
          <Routes>
            <Route path="/">
              <Route index element={<HomePage1 />} />
              <Route path="home-1" element={<HomePage1 />} />

              {/* Rotas do Dashboard */}
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="dshb-listing" element={<DshbListingPage />} />
              <Route path="dshb-settings" element={<DshbSettingsPage />} />
              <Route path="dshb-administration" element={<DshbAdministrationPage />}/>
              <Route path="dshb-planejamento" element={<DshbAssignmentPage />} />
              <Route path="dshb-calendar" element={<DshbCalenderPage />} />
              <Route path="dshb-notas" element={<DshbDashboardPage />} />
              <Route path="dshb-emprestimo" element={<DshbDictionaryPage />} />
              <Route path="dshb-reservas" element={<DshbReservasPage />} />

              {/* Rotas de Autenticação */}
              <Route path="login" element={<LoginPage />} />

              <Route path="esqueci-senha" element={<ForgotPasswordPage />} />
              
              {/* ROTA ATUALIZADA para aceitar o token na URL */}
              <Route path="resetar-senha/:token" element={<ResetPasswordPage />} />

              {/* Rotas de Erro */}
              <Route path="not-found" element={<NotFoundPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
          <ScrollTopBehaviour />
        </BrowserRouter>
      </Context>
    </>
  );
}

export default App;
