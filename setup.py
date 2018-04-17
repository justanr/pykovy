from setuptools import setup, find_packages


if __name__ == "__main__":
    setup(
        name="pykovy",
        version="1.1",
        author="Alec Nikolas Reiter",
        author_email="alecreiter@gmail.com",
        description="Real simple markov chains",
        zip_safe=False,
        url="https://github.com/justanr/pykovy",
        packages=find_packages('src'),
        package_dir={'': 'src'},
        keywords=["markov"],
        license="MIT",
        classifiers=[
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: 3.6"
        ]
    )
