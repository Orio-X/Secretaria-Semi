// import HomeOne from "@/components/homes/home";
import Header from "@/components/layout/headers/Header";

import HomeHero from "@/components/homes/heros/HomeHero";

import FeaturesOne from "@/components/homes/features/FeaturesOne";
import FooterOne from "@/components/layout/footers/FooterOne";
import Preloader from "@/components/common/Preloader";

import MetaComponent from "@/components/common/MetaComponent";

const metadata = {
  title:
    "SkyPen",
  description:
    "Eleve sua experiência de gerenciamento de secretaria integrada com nosso sistema intuitivo e eficiente.",
};

export default function HomePage1() {
  return (
    <>
      <Preloader />
      <MetaComponent meta={metadata} />
      <Header />

      <div className="content-wrapper  js-content-wrapper overflow-hidden">
        <HomeHero />
        <FeaturesOne />
        <FooterOne />
      </div>
    </>
  );
}
