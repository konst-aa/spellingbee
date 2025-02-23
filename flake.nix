{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    linuxPkgs = nixpkgs.legacyPackages.x86_64-linux;
    darwinPkgs = nixpkgs.legacyPackages.aarch64-darwin;
    deps = pkgs: [
      pkgs.python3
      pkgs.python3Packages.pygame
      pkgs.makeWrapper
    ];
    deriv = pkgs:
      pkgs.stdenv.mkDerivation {
      pname = "spellingbee";
      version = "0.0.0";
      src = ./.;
      buildInputs = deps pkgs;
      installPhase = ''
        mkdir -p $out/bin
        mkdir -p $out/etc

        cp *.ttf $out/etc
        cp games.json $out/etc
        cp main.py $out/bin/spellingbee

        for f in $out/bin/*
        do 
          wrapProgram $f \
           --set SPELLINGBEE_ETC $out/etc/
        done
      '';
    };
  in {
    packages.x86_64-linux.spellingbee = deriv linuxPkgs;
    packages.aarch64-darwin.spellingbee = deriv darwinPkgs;

    packages.x86_64-linux.default = self.packages.x86_64-linux.spellingbee;
    packages.aarch64-darwin.default = self.packages.aarch64-darwin.spellingbee;


    devShells.x86_64-linux.default = linuxPkgs.mkShell {
      buildInputs = deps linuxPkgs;
    };

  };
}
