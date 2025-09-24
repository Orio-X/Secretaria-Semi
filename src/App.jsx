import "./styles/index.scss";

import "@fortawesome/fontawesome-svg-core/styles.css";
import "react-calendar/dist/Calendar.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import AOS from "aos";
import "aos/dist/aos.css";
import { useEffect } from "react"; // Removido o useState que não era mais usado
import Context from "@/context/Context";

// Importe suas páginas
import HomePage1 from "./pages";
import DashboardPage from "./pages/dashboard/dashboard";
import DshbListingPage from "./pages/dashboard/dshb-listing";
import DshbSettingsPage from "./pages/dashboard/dshb-settings";
import DshbAdministrationPage from "./pages/dashboard/dshb-administration";
import DshbAssignmentPage from "./pages/dashboard/dshb-assignment";
import DshbCalenderPage from "./pages/dashboard/dshb-calendar";
import DshbDashboardPage from "./pages/dashboard/dshb-dashboard";
import DshbDictionaryPage from "./pages/dashboard/dshb-dictionary";
import DshbForumsPage from "./pages/dashboard/dshb-forums";
import DshbGradesPage from "./pages/dashboard/dshb-grades";
import DshbMessagesPage from "./pages/dashboard/dshb-messages";
import DshbPartcipentPage from "./pages/dashboard/dshb-participants";
import DshbQuizPage from "./pages/dashboard/dshb-quiz";

import LoginPage from "./pages/others/login";
import SignupPage from "./pages/others/signup";
import ScrollTopBehaviour from "./components/common/ScrollTopBehaviour";
import NotFoundPage from "./pages/not-found";

function App() {
  // REMOVIDO: A busca de dados de 'alunos' foi retirada para melhorar a performance.
  // Ela deve ser feita dentro do componente que precisa da lista (ex: DshbPartcipentPage).

  useEffect(() => {
    AOS.init({
      duration: 700,
      offset: 120,
      easing: "ease-out",
      once: true,
    });
  }, []);

  return (
    <>
      <Context>
        <BrowserRouter>
          {/* A estrutura de rotas voltou a ser a original, mais simples, sem a proteção. */}
          <Routes>
            <Route path="/">
              <Route index element={<HomePage1 />} />
              <Route path="home-1" element={<HomePage1 />} />

              {/* Todas as rotas do dashboard estão abertas novamente */}
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="dshb-listing" element={<DshbListingPage />} />
              <Route path="dshb-settings" element={<DshbSettingsPage />} />
              <Route
                path="dshb-administration"
                element={<DshbAdministrationPage />}
              />
              {/* ROTA ATUALIZADA: A rota da tarefa agora é dinâmica, como queríamos. */}
              <Route path="dshb-assignment" element={<DshbAssignmentPage />} />
              <Route path="dshb-calendar" element={<DshbCalenderPage />} />
              <Route path="dshb-dashboard" element={<DshbDashboardPage />} />
              <Route path="dshb-dictionary" element={<DshbDictionaryPage />} />
              <Route path="dshb-forums" element={<DshbForumsPage />} />
              <Route path="dshb-grades" element={<DshbGradesPage />} />
              <Route path="dshb-messages" element={<DshbMessagesPage />} />
              <Route
                path="dshb-participants"
                element={<DshbPartcipentPage />}
              />
              <Route path="dshb-quiz" element={<DshbQuizPage />} />

              <Route path="not-found" element={<NotFoundPage />} />
              <Route path="*" element={<NotFoundPage />} />
              <Route path="login" element={<LoginPage />} />
              <Route path="signup" element={<SignupPage />} />
            </Route>
          </Routes>
          <ScrollTopBehaviour />
        </BrowserRouter>
      </Context>
    </>
  );
}

export default App;