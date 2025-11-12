// src/components/layout/footers/FooterNine.jsx

import React from "react";


//apenas um rodapé basico com direitos autorais da org
export default function FooterNine() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="py-30 border-top-light">
          <div className="row items-center justify-between">
            <div className="col-auto">
              <div className="text-13 lh-1">
                © {new Date().getFullYear()} SkyPen. Todos os direitos reservados.
              </div>
            </div>

            <div className="col-auto">
              <div className="d-flex items-center">
                <div className="d-flex items-center flex-wrap x-gap-20">
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
