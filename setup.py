from setuptools import setup,find_packages

setup(
    name='ppmonitor',
    version='0.0.1_beta',
    packages=find_packages(),
    url='https://github.com/ChenYuelong/ppmonitor',
    license='',
    author='yuelong.chen',
    author_email='yuelong.chen@oumeng.com.cn',
    description='ppmonitor：监控程序内存使用情况',
    scripts=['ppmonitor.py']
)
