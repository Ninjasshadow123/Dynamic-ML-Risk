import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Layout from "./components/Layout";
import FieldConfiguration from "./pages/FieldConfiguration";
import Machines from "./pages/Machines";
import RiskPrediction from "./pages/RiskPrediction";


function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route
          path="/"
          element={
            <Navigate
              to="/machines"
              replace
            />
          }
        />

        <Route
          path="/fields"
          element={<FieldConfiguration />}
        />

        <Route
          path="/machines"
          element={<Machines />}
        />

        <Route
          path="/prediction"
          element={<RiskPrediction />}
        />
      </Route>
    </Routes>
  );
}


export default App;